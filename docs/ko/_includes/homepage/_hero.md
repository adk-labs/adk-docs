<!-- Hero Section -->
<div class="hero-grid">
  <div class="hero-content">
    <h1>프로토타입이 아니라 <span class="hero-punchline">프로덕션 에이전트를 구축하세요.</span></h1>
    <p>ADK는 신뢰할 수 있는 AI 에이전트를 엔터프라이즈 규모로 구축, 디버그, 배포할 수 있게 해 주는 오픈소스 에이전트 개발 프레임워크입니다. Python, TypeScript, Go, Java, Kotlin을 지원합니다.</p>
    <div class="hero-actions">
      <a href="get-started/" class="btn btn-primary">시작하기</a>
      <!-- <a href="skills/" class="btn btn-accent">에이전트 스킬</a> -->
    </div>
  </div>
  <div class="hero-visual">
    <!-- Tabbed Code Window -->
    <div class="tabbed-area" id="tabbed-area">
      <div class="mac-window">
        <div class="iterm-tab-bar">
          <div class="iterm-tab active" data-lang="python">Python</div>
          <div class="iterm-tab" data-lang="typescript">TypeScript</div>
          <div class="iterm-tab" data-lang="go">Go</div>
          <div class="iterm-tab" data-lang="java">Java</div>
          <div class="iterm-tab" data-lang="kotlin">Kotlin</div>
        </div>
<div class="code-content" id="code-python"><pre><span class="kw">from</span> google.adk <span class="kw">import</span> <span class="fn">Agent</span>
<span class="kw">from</span> google.adk.tools <span class="kw">import</span> google_search

agent = <span class="fn">Agent</span>(
    name=<span class="str">"researcher"</span>,
    model=<span class="str">"gemini-flash-latest"</span>,
    instruction=<span class="str">"You help users research topics thoroughly."</span>,
    tools=[google_search],
)</pre></div>

<div class="code-content" id="code-typescript" style="display:none"><pre><span class="kw">import</span> { <span class="fn">LlmAgent, GOOGLE_SEARCH</span> } <span class="kw">from</span> <span class="str">'@google/adk'</span>;

<span class="kw">const</span> agent = <span class="kw">new</span> <span class="fn">LlmAgent</span>({
  name: <span class="str">'researcher'</span>,
  model: <span class="str">'gemini-flash-latest'</span>,
  instruction: <span class="str">'You help users research topics thoroughly.'</span>,
  tools: [GOOGLE_SEARCH],
});

</pre></div>

<div class="code-content" id="code-go" style="display:none"><pre><span class="kw">import</span> <span class="str">"google.golang.org/adk/v2/agent/llmagent"</span>

model, _ := gemini.<span class="fn">NewModel</span>(context.<span class="fn">Background</span>(), <span class="str">"gemini-flash-latest"</span>, <span class="kw">nil</span>)
a, _ := llmagent.<span class="fn">New</span>(llmagent.<span class="fn">Config</span>{
    Name:        <span class="str">"researcher"</span>,
    Model:       model,
    Instruction: <span class="str">"You help users research topics thoroughly."</span>,
    Tools:       []tool.Tool{geminitool.<span class="fn">GoogleSearch</span>{}},
})</pre></div>

<div class="code-content" id="code-java" style="display:none"><pre><span class="kw">import</span> com.google.adk.agents.<span class="fn">LlmAgent</span>;
<span class="kw">import</span> com.google.adk.tools.<span class="fn">GoogleSearchTool</span>;

<span class="fn">LlmAgent</span> agent = <span class="fn">LlmAgent</span>.builder()
    .name(<span class="str">"researcher"</span>)
    .model(<span class="str">"gemini-flash-latest"</span>)
    .instruction(<span class="str">"You help users research topics thoroughly."</span>)
    .tools(<span class="kw">new</span> <span class="fn">GoogleSearchTool()</span>)
    .build();</pre></div>

<div class="code-content" id="code-kotlin" style="display:none"><pre><span class="kw">import</span> com.google.adk.kt.agents.<span class="fn">LlmAgent</span>
<span class="kw">import</span> com.google.adk.kt.tools.<span class="fn">GoogleSearchTool</span>

<span class="kw">val</span> agent = <span class="fn">LlmAgent</span>(
    name = <span class="str">"researcher"</span>,
    model = <span class="fn">Gemini</span>(name = <span class="str">"gemini-flash-latest"</span>),
    instruction = <span class="fn">Instruction</span>(<span class="str">"You help users research topics thoroughly."</span>),
    tools = listOf(<span class="fn">GoogleSearchTool</span>()),
)</pre></div>

</div>
      <!-- Install info synced with tabs -->
      <div class="install-info" id="install-python">
        <div class="install-cmd">
          <code>pip install google-adk</code>
          <button class="copy-btn" data-copy="pip install google-adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-typescript" style="display:none">
        <div class="install-cmd">
          <code>npm install @google/adk</code>
          <button class="copy-btn" data-copy="npm install @google/adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-go" style="display:none">
        <div class="install-cmd">
          <code>go get google.golang.org/adk/v2</code>
          <button class="copy-btn" data-copy="go get google.golang.org/adk/v2" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-java" style="display:none">
        <div class="install-cmd">
          <code>com.google.adk:google-adk</code>
          <button class="copy-btn" data-copy="com.google.adk:google-adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-kotlin" style="display:none">
        <div class="install-cmd">
          <code>com.google.adk:google-adk-kotlin-core</code>
          <button class="copy-btn" data-copy="com.google.adk:google-adk-kotlin-core" title="Copy to clipboard">📋</button>
        </div>
      </div>
    </div>
  </div>
</div>
