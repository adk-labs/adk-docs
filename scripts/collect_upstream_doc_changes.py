#!/usr/bin/env python3

"""Collect markdown document changes from an upstream repository."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Sequence


UTC = dt.timezone.utc


@dataclasses.dataclass
class ChangeSet:
    added: list[str]
    modified: list[str]
    deleted: list[str]
    renamed: list[tuple[str, str]]

    @property
    def total(self) -> int:
        return len(self.added) + len(self.modified) + len(self.deleted) + len(self.renamed)


def run_git(cwd: pathlib.Path, args: Sequence[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (
            f"git {' '.join(args)} failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
        raise RuntimeError(message)
    return result.stdout.strip()


def ensure_remote(cwd: pathlib.Path, remote_name: str, remote_url: str) -> None:
    remotes = run_git(cwd, ["remote"]).splitlines()
    if remote_name not in remotes:
        run_git(cwd, ["remote", "add", remote_name, remote_url])
        return

    current_url = run_git(cwd, ["remote", "get-url", remote_name])
    if current_url != remote_url:
        run_git(cwd, ["remote", "set-url", remote_name, remote_url])


def load_state(state_file: pathlib.Path) -> dict[str, str]:
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in state file: {state_file}") from exc


def save_state(state_file: pathlib.Path, state: dict[str, str]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha_exists(cwd: pathlib.Path, sha: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def parse_diff_name_status(diff_text: str) -> ChangeSet:
    changes = ChangeSet(added=[], modified=[], deleted=[], renamed=[])
    for raw_line in diff_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        code = status[0]

        if code == "A" and len(parts) >= 2:
            changes.added.append(parts[1])
        elif code == "M" and len(parts) >= 2:
            changes.modified.append(parts[1])
        elif code == "D" and len(parts) >= 2:
            changes.deleted.append(parts[1])
        elif code == "R" and len(parts) >= 3:
            changes.renamed.append((parts[1], parts[2]))

    changes.added.sort()
    changes.modified.sort()
    changes.deleted.sort()
    changes.renamed.sort(key=lambda pair: (pair[0], pair[1]))
    return changes


def to_http_url(remote_url: str) -> str | None:
    if remote_url.startswith("https://github.com/"):
        return remote_url.removesuffix(".git")
    if remote_url.startswith("git@github.com:"):
        return f"https://github.com/{remote_url[len('git@github.com:'):].removesuffix('.git')}"
    return None


def build_compare_url(remote_url: str, start_sha: str, end_sha: str) -> str | None:
    base = to_http_url(remote_url)
    if not base:
        return None
    if start_sha == end_sha:
        return f"{base}/commit/{end_sha}"
    return f"{base}/compare/{start_sha}...{end_sha}"


def format_list(items: Sequence[str]) -> str:
    if not items:
        return "- (none)\n"
    return "".join(f"- `{item}`\n" for item in items)


def format_renamed(items: Sequence[tuple[str, str]]) -> str:
    if not items:
        return "- (none)\n"
    return "".join(f"- `{old}` -> `{new}`\n" for old, new in items)


def ensure_log_header(log_file: pathlib.Path) -> None:
    if log_file.exists():
        return
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("# Upstream Document Change Log\n\n", encoding="utf-8")


def append_log_entry(
    *,
    log_file: pathlib.Path,
    now_utc: dt.datetime,
    remote_url: str,
    remote_name: str,
    branch: str,
    previous_sha: str,
    current_sha: str,
    compare_url: str | None,
    commit_count: int,
    pathspecs: Sequence[str],
    changes: ChangeSet,
    note: str | None,
) -> None:
    ensure_log_header(log_file)
    lines: list[str] = [
        f"## {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        f"- Upstream: `{remote_url}` (`{remote_name}/{branch}`)",
        f"- Compared range: `{previous_sha}` -> `{current_sha}`",
        f"- Upstream commit count in range: {commit_count}",
        f"- Tracked paths: {', '.join(f'`{p}`' for p in pathspecs)}",
        f"- Markdown file changes: {changes.total}",
    ]
    if compare_url:
        lines.append(f"- Compare URL: {compare_url}")
    if note:
        lines.append(f"- Note: {note}")
    lines.extend(
        [
            "",
            "### Added",
            format_list(changes.added).rstrip(),
            "",
            "### Modified",
            format_list(changes.modified).rstrip(),
            "",
            "### Deleted",
            format_list(changes.deleted).rstrip(),
            "",
            "### Renamed",
            format_renamed(changes.renamed).rstrip(),
            "",
            "---",
            "",
        ]
    )

    with log_file.open("a", encoding="utf-8") as fp:
        fp.write("\n".join(lines))


def bootstrap_previous_sha(
    *,
    cwd: pathlib.Path,
    current_sha: str,
    bootstrap_hours: int,
    now_utc: dt.datetime,
) -> tuple[str, str | None]:
    before_time = now_utc - dt.timedelta(hours=bootstrap_hours)
    before_arg = before_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    candidate = run_git(cwd, ["rev-list", "-1", f"--before={before_arg}", current_sha])
    if candidate and candidate != current_sha:
        note = (
            "State file did not exist. "
            f"Bootstrapped from commit that existed {bootstrap_hours}h ago."
        )
        return candidate, note

    return current_sha, "State file did not exist and no earlier commit was found."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect upstream markdown document changes and append a daily markdown report."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path where git commands are executed. Default: current directory.",
    )
    parser.add_argument(
        "--remote-name",
        default="upstream",
        help="Remote name for upstream repository. Default: upstream.",
    )
    parser.add_argument(
        "--upstream-url",
        default="https://github.com/google/adk-docs.git",
        help="Upstream repository URL.",
    )
    parser.add_argument(
        "--upstream-branch",
        default="main",
        help="Upstream branch name. Default: main.",
    )
    parser.add_argument(
        "--state-file",
        default=".github/upstream-doc-change-log/state.json",
        help="Path to JSON state file (relative to repo root).",
    )
    parser.add_argument(
        "--log-dir",
        default="upstream-doc-change-log",
        help="Directory for generated markdown logs (relative to repo root).",
    )
    parser.add_argument(
        "--bootstrap-hours",
        type=int,
        default=24,
        help="On first run, compare against commit from this many hours ago. Default: 24.",
    )
    parser.add_argument(
        "--pathspec",
        action="append",
        default=[],
        help=(
            "Git pathspec to track. Can be repeated. "
            "Default tracks all markdown files and excludes generated log directories."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(args.repo_root).resolve()
    state_file = repo_root / args.state_file
    now_utc = dt.datetime.now(UTC)
    log_dir = repo_root / args.log_dir
    log_file = log_dir / f"{now_utc.strftime('%Y-%m-%d')}.md"
    pathspecs = args.pathspec or [
        ":(glob)**/*.md",
        ":(exclude)upstream-doc-change-log/**",
        ":(exclude).github/upstream-doc-change-log/**",
    ]

    ensure_remote(repo_root, args.remote_name, args.upstream_url)
    run_git(repo_root, ["fetch", "--no-tags", args.remote_name, args.upstream_branch])

    current_sha = run_git(repo_root, ["rev-parse", f"{args.remote_name}/{args.upstream_branch}"])
    state = load_state(state_file)
    previous_sha = state.get("last_upstream_sha", "")
    note: str | None = None

    if previous_sha and not sha_exists(repo_root, previous_sha):
        previous_sha = ""
        note = "Stored SHA in state file does not exist locally. Rebootstrapped baseline."

    if not previous_sha:
        previous_sha, bootstrap_note = bootstrap_previous_sha(
            cwd=repo_root,
            current_sha=current_sha,
            bootstrap_hours=args.bootstrap_hours,
            now_utc=now_utc,
        )
        note = f"{note} {bootstrap_note}".strip() if note else bootstrap_note

    if previous_sha == current_sha:
        diff_text = ""
        commit_count = 0
    else:
        diff_text = run_git(
            repo_root,
            [
                "diff",
                "--name-status",
                "--find-renames",
                f"{previous_sha}..{current_sha}",
                "--",
                *pathspecs,
            ],
        )
        commit_count = int(run_git(repo_root, ["rev-list", "--count", f"{previous_sha}..{current_sha}"]) or "0")

    changes = parse_diff_name_status(diff_text)
    compare_url = build_compare_url(args.upstream_url, previous_sha, current_sha)
    append_log_entry(
        log_file=log_file,
        now_utc=now_utc,
        remote_url=args.upstream_url,
        remote_name=args.remote_name,
        branch=args.upstream_branch,
        previous_sha=previous_sha,
        current_sha=current_sha,
        compare_url=compare_url,
        commit_count=commit_count,
        pathspecs=pathspecs,
        changes=changes,
        note=note,
    )

    new_state = {
        "last_checked_at_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_upstream_sha": current_sha,
        "upstream_branch": args.upstream_branch,
        "upstream_remote_name": args.remote_name,
        "upstream_url": args.upstream_url,
    }
    save_state(state_file, new_state)

    print(f"Log file: {log_file}")
    print(f"Current upstream SHA: {current_sha}")
    print(f"Markdown changes in this run: {changes.total}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
