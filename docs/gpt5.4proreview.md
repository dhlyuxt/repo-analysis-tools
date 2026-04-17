明白了。那这件事的正确方向不是“重构旧仓库”，而是**新开一个仓库，把旧仓库当作能力矿区、行为参考和测试金标准**。你现在的旧仓库一边已经接受了 “Scope-First / Slice-First / Agent-Centric” 的新设计，一边又还保留着旧时代的 `agent_runtime`、`answers`、`retrieval`、`index/export/analyze` 兼容路径，以及把索引落在 `<repo>/.claude/codewiki/index.db` 这种强绑定 Claude 的运行态设计；这几套心智模型混在一起，本身就会持续放大复杂度。README、包结构和 active spec 都能看出这种“新旧并存”的状态。

我给你的建议是：

**旧仓库冻结为参考实现，新仓库从零开始，只继承三样东西：**

1. 已被验证有价值的**确定性分析能力**；
2. 已被验证合理的**工具边界**；
3. 旧仓库里的 **fixtures / tests / spec**，把它们当成迁移验收标准。旧仓库现在已经有按域拆分的 `scan / scope / anchors / slices / evidence / impact / reporting / storage`，以及相对完整的测试目录，这非常适合拿来做“行为对照”，但不适合整包平移。

------

## 一、先把目标重新定义清楚

新仓库的产品定义应该是：

**“本地代码仓库的确定性分析内核 + 一个本地 MCP server + 一套同时服务 Claude Code 和 Codex 的 Skills。”**

而不是：

**“一个自带会话管理、自己做 agent 编排、自己控制大模型工作流的代码阅读应用。”**

原因很直接。你旧仓库的 active spec 已经明确否定了“whole-repo offline artifact + 统一分析流水线”这条路，转向 query-driven、scope-first、facts-first、bounded expansion；它还明确把 agent 的职责压缩为“基于切片解释事实”，而不是让 server 自己接管完整问答。

所以新仓库的总原则应该定成这四句：

- **Server 只提供事实，不提供最终解释。**
- **解释留给 Claude Code / Codex，分析留给本地内核。**
- **所有能力都围绕 slice/evidence 工作，不再做 whole-repo 大产物。**
- **先支持本地 stdio MCP，再考虑 HTTP。**

Claude Code 和 Codex 目前都支持接 MCP，也都支持 Skills 的渐进加载；Claude Code 项目级 MCP 用 `.mcp.json`，Codex 项目级 MCP 用受信任项目下的 `.codex/config.toml`，两边都能把 skill 放在仓库里随项目一起分发。

------

## 二、新仓库应该长什么样

我建议新仓库不要再叫 `codewiki`，避免和旧仓库、以及 FSoft 的上游 CodeWiki 混淆。名字上可以用 `mycodewiki-next`、`mycodewiki-mcp` 这类过渡名，等稳定后再收敛。

结构上，建议只有三层：

### 1）分析内核层

只保留这些域：

- `scan`
- `scope`
- `anchors`
- `slice`
- `evidence`
- `impact`
- `report`
- `store`

这里面不允许出现任何模型调用、会话状态、prompt orchestration。它们只负责产生**结构化事实**。这正是旧 spec 想保住的主线。

### 2）MCP server 层

这层只做两件事：

- 把分析能力暴露成 MCP tools；
- 管理轻量会话句柄、返回 contract、做边界校验。

官方 MCP Python SDK 现在已经是 Tier 1，支持 tools/resources/prompts，也支持 stdio 和 Streamable HTTP；用 `FastMCP` 起本地 server 就够了，没必要自己再造一层协议适配器。

### 3）Skills 分发层

这层不放业务逻辑，只放“面向客户端的工作流说明”。

- Claude Code 的技能放 `.claude/skills/<name>/SKILL.md`
- Codex 的技能放 `.agents/skills/<name>/SKILL.md`
- 两边都依赖 `description` 做自动匹配；Claude 还支持 `allowed-tools`，Codex 还支持在 `agents/openai.yaml` 里声明 MCP 依赖和 invocation 策略。

这意味着你应该维护一份 `skills-src/` 作为真源，再生成 Claude/Codex 两套输出，而不是手工维护两份几乎相同的 skill。

------

## 三、旧仓库里哪些该吸收，哪些不要碰

### 应该吸收的

第一类是**概念和边界**。

旧 spec 已经把边界划得很清楚：
 Phase 1 做 scope 和文件角色；Phase 2 做 tree-sitter anchor facts；Phase 3 做 query-time slice planner；Phase 4 做 agent-facing ask/impact；Phase 5 做 focused report。这套分层是正确的，新仓库直接继承。

第二类是**工具边界**。

旧仓库虽然 orchestration 太重，但内部 tool registry 已经暴露出一组很合适的能力边界：`scan_repo`、`plan_slice`、`expand_slice`、`read_evidence_pack`、`get_repo_freshness`、`impact_from_paths`、`render_focus_report`、`open_span`。这恰恰说明你真正需要发布的是“工具合同”，而不是“旧聊天运行时”。

第三类是**解析子模块和测试资产**。

旧 spec 明确说过要保留并适配一部分 tree-sitter 基础设施、少量 markdown export helper，以及从 FSoft CodeWiki 里选择性 vendoring 一小段 C 相关分析模块；同时把 `IndexBuilder`、旧 symbol extraction flow、旧 ask/impact context construction 重写掉。这个判断我建议原封不动继承到新仓库。FSoft 上游仓库本身也是一个 repo-level 文档框架，所以你只能拿它的窄子集，不能继承它的整体工作流。

### 只当参考，不直接搬代码的

- `ask`
- `answers`
- `retrieval`
- `cli` 的旧交互壳
- `agent_runtime`

这些目录可以拿来理解行为，但不应该原样迁移，因为它们最容易把旧的 agent 编排心智模型重新带回来。旧仓库里 `ask` 本身就是把 slice planning 和 context packing 又重新包成一个大问答入口，这在新架构里不该成为主入口。

### 应该直接丢掉的

- 自研会话 orchestrator
- 对 Claude Agent SDK 的主路径依赖
- whole-repo `analyze/export` 主工作流
- `faiss-cpu`、`chromadb` 这类会把系统重新拖回“大索引 / 大检索 / 大编排”路线的依赖，至少不该进 V1 主包

旧 requirements 里这些依赖仍然在，说明旧工程还背着过去的实验负担；新仓库的主线应收敛到 tree-sitter、pathspec、networkx、rapidfuzz、sqlite 这类必要集合。

------

## 四、新仓库的推荐目录

我建议直接按这个骨架开仓：

```
mycodewiki-mcp/
  pyproject.toml
  README.md
  docs/
    architecture.md
    contracts/
      tool-scan-repo.md
      tool-plan-slice.md
      tool-read-evidence-pack.md
    harvest/
      old-repo-inventory.md
      migration-decisions.md

  src/mycodewiki/
    core/
      models/
      store/
      errors.py

    scan/
    scope/
    anchors/
    slice/
    evidence/
    impact/
    report/

    mcp/
      server.py
      tools.py
      contracts.py
      session.py
      guards.py

    install/
      claude.py
      codex.py
      skills_gen.py

    cli/
      main.py

  third_party/
    fsoft_codewiki_c/

  skills-src/
    repo-ask/
      SKILL.md
      meta.claude.yml
      meta.codex.yml
    repo-impact/
      SKILL.md
      meta.claude.yml
      meta.codex.yml
    repo-scan-refresh/
      SKILL.md
      meta.claude.yml
      meta.codex.yml
    repo-focus-report/
      SKILL.md
      meta.claude.yml
      meta.codex.yml
    repo-scope-explain/
      SKILL.md
      meta.claude.yml
      meta.codex.yml

  tests/
    fixtures/
    golden/
    unit/
    e2e/
```

这里有两个关键点：

**第一，运行态目录统一叫 `.codewiki/`。**
 旧 README 里 `scan` 把索引放在 `<repo>/.claude/codewiki/index.db`，但 active spec 又已经用 `.codewiki/scope.yml` 作为配置来源。新仓库必须改成中立的 `.codewiki/`，否则天然偏向 Claude，不适合双客户端。

**第二，`third_party/` 只存窄 vendoring。**
 不要把旧仓库 subtree 进去；也不要把 FSoft 整仓拉进来。只 vendoring 那几个被 spec 明确点名、你确实需要的 C 分析子模块。

------

## 五、MCP 工具面应该怎么设计

V1 我建议只公开 9 个工具：

- `scan_repo`
- `show_scope`
- `plan_slice`
- `expand_slice`
- `read_evidence_pack`
- `get_repo_freshness`
- `open_span`
- `impact_from_paths`
- `render_focus_report`

这样做的原因是：旧 runtime 已经证明这组边界自然、可组合，而且是围绕 slice/evidence 组织的；你没必要再造一个“万能问答工具”。

### 一个很重要的决定：不要公开 `ask_question` 这种 mega-tool

`ask` 应该是 skill 的工作流，不应该是 server 的主能力。

也就是说：

- MCP server 负责：扫描、切片、证据包、精确 span 打开、影响分析、报告导出；
- Claude Code / Codex 负责：读证据、组织解释、补充自然语言回答。

这正好和旧 spec 里“facts before explanations”“bounded second expansion”“agent distinguishes hard facts / interpretation / unknowns”的方向一致。

### 每个工具的返回合同建议统一

统一成这个形状：

```
{
  "schema_version": "1",
  "status": "ok",
  "data": {},
  "guidance": [],
  "recommended_next_tools": []
}
```

再加一个原则：

- **有持久 ID 的地方，一律返回 stable ID + session handle。**

旧 registry 已经在 `plan_slice` / `expand_slice` 里持久化 `slice_run_id`，并生成 `manifest_handle`；`read_evidence_pack` 里持久化 `evidence_pack_id`，并返回 `evidence_handle`。这说明“稳定 ID + 会话句柄”是个已经验证过的设计，新仓库直接延续。

### `open_span` 必须保留强约束

旧实现做得对的地方一定要保留：

- 只能基于 evidence pack 已选文件读取；
- 必须带 `span_id` 或明确的 file/line 区间；
- 有严格行数上限。

这是防止 MCP server 退化成“无限读整个仓库”的关键闸门。

### `get_repo_freshness` 要成为每个 skill 的前置工具

旧实现里已经有 `missing_scan / stale / ok` 这三种状态，还会检查 drifted file / span。这个工具在双客户端世界里比旧 chat runtime 更重要，因为 skill 必须先知道索引是否还可信。

------

## 六、Skills 应该怎么组织

### 先只做 5 个 skill

1. `repo-ask`
    处理“定义在哪”“这个函数怎么工作”“某 feature 涉及哪些文件”。
2. `repo-impact`
    处理“改这几个文件会影响哪里”。
3. `repo-scan-refresh`
    处理 missing / stale 时的重扫。
4. `repo-focus-report`
    处理 symbol/file/topic 的 focused report 输出。
5. `repo-scope-explain`
    解释 scope、file role、why included/ignored。

### `repo-ask` 的工作流应该写死为：

1. `get_repo_freshness`
2. 必要时 `scan_repo`
3. `plan_slice`
4. `read_evidence_pack`
5. 真需要时 `open_span`
6. 回答时分三段：
   - Hard facts
   - Local inference
   - Unknowns

这不是拍脑袋，而是直接顺着旧 spec 的“query-local context”“facts before explanations”“bounded expansion”走。

### Claude 和 Codex 的 skill 要分别生成，不要共用同一目录

因为两边的技能目录和元数据机制不同：

- Claude Code：`.claude/skills/...`，支持 `allowed-tools`、`disable-model-invocation`、`user-invocable` 等 frontmatter。
- Codex：`.agents/skills/...`，支持 `agents/openai.yaml` 提供 UI metadata、MCP dependency、隐式调用策略。

所以更合理的做法是：

- `skills-src/` 维护正文；
- 生成器把它渲染成两套产物；
- 两边只在 metadata 层做差异化。

### 有副作用的 skill 默认不要隐式触发

像 `repo-scan-refresh`、`repo-focus-report` 这种会写索引或写文件的 skill，应该默认只允许显式调用。

- Claude 侧可以利用 invocation 控制；
- Codex 侧可以用 `allow_implicit_invocation: false`。

------

## 七、MCP 配置和安装方式

新仓库里应该自带一个小安装器，而不是让用户手写配置。

例如：

- `mycodewiki init --client claude-code`
- `mycodewiki init --client codex`

它分别写入：

- Claude Code 的项目级 `.mcp.json`
- Codex 的项目级 `.codex/config.toml`
- 对应客户端的 skills 目录
- 一个 `.codewiki/scope.yml` 模板

这是因为两边的项目级 MCP 配置路径本来就不同，但都支持“仓库内分发”。Claude 用 `.mcp.json`；Codex 用受信任项目下的 `.codex/config.toml`。

Claude 的模板可以长这样：

```
{
  "mcpServers": {
    "mycodewiki": {
      "command": "uv",
      "args": ["run", "python", "-m", "mycodewiki.mcp.server"]
    }
  }
}
```

Codex 的模板可以长这样：

```
[mcp_servers.mycodewiki]
command = "uv"
args = ["run", "python", "-m", "mycodewiki.mcp.server"]
```

------

## 八、安全边界要从第一天就定死

这部分很重要，因为 MCP server 一旦做成“本地工具集合”，边界不清就会变成仓库读写大后门。

官方 MCP 安全建议和 Claude Code 文档都指向同一件事：
 **本地 server 优先 stdio、最小权限、限制 filesystem/network/system access，并且对第三方或不可信内容保持 prompt injection 警惕。** Claude Code 对第三方 MCP server 也明确提醒了这类风险。Roots 机制可以帮助 server 理解客户端允许的目录，但 server 自己仍然必须做边界校验。

所以我建议 V1 的安全策略直接写成：

- 只支持本地 `stdio` transport；
- 默认只读；
- 不提供任意 shell 执行；
- 不提供任意网络访问；
- 所有 path 都必须落在 repo root 或 MCP roots 允许范围内；
- `open_span` 只读已选 evidence 文件；
- `render_focus_report` 只能写到 `.codewiki/reports/` 或 `docs/codewiki/` 白名单目录；
- 任何“重扫整个仓库”的动作都必须显式触发。

------

## 九、我建议你按这 7 个阶段开新仓

### 阶段 0：冻结旧仓库，做 Harvest

不要先写代码。先把旧仓库“拆解成资产清单”。

产出物只要三份：

- `old-repo-inventory.md`
- `migration-decisions.md`
- `acceptance-cases.md`

这里面把旧 spec、现有工具边界、fixtures/tests、可复用模块、必须重写模块全部列清楚。旧 spec 里已经给过一份 keep/rewrite/freeze 的初版判断，可以直接作为这一步的起点。

### 阶段 1：搭新仓骨架和 contract

先把这些定死：

- `.codewiki/` 运行态目录
- SQLite store schema
- 工具返回 contract
- error taxonomy
- session handle 设计

这一步不要做 LLM，不要做 skills，只把“内核和接口”框起来。

### 阶段 2：实现 `scan` + `scope`

先打通：

- repo discovery
- role classification
- `.codewiki/scope.yml`
- `scan_repo`
- `show_scope`
- `get_repo_freshness`

旧 spec 里 scope 阶段本来就是 Phase 1，而且旧 README 也把 `scan` / `scope show` 放在最前。

### 阶段 3：实现 `anchors`

这里才开始吸收 tree-sitter 和 FSoft 的窄子集。

V1 只做旧 spec 已经圈定的 facts：

- files
- function defs/decls
- struct/typedef/enum names
- include edges
- call edges
- macros
- conditionals
- declaration spans / raw texts
- `parse_status = exact | partial | unresolved`

不要碰 canonical type resolution。旧 spec 明确说 V1 不做这个。

### 阶段 4：实现 `slice` / `evidence` / `impact` / `report`

把 query-time planner 和 evidence pack 建起来，再补：

- `plan_slice`
- `expand_slice`
- `read_evidence_pack`
- `open_span`
- `impact_from_paths`
- `render_focus_report`

这里是产品真正开始“像代码阅读助手”的地方。

### 阶段 5：挂 MCP server

用官方 Python SDK 的 `FastMCP` 暴露工具。V1 只上 stdio。

### 阶段 6：做 skills 生成器和 init 安装器

把 `skills-src/` 渲染为：

- `.claude/skills/...`
- `.agents/skills/...`

再加 `init --client ...` 命令写配置文件。

### 阶段 7：做双客户端 E2E

最少验证这三条链：

- Claude Code + `.mcp.json` + `.claude/skills/`
- Codex + `.codex/config.toml` + `.agents/skills/`
- 两边都能完成 `repo-ask` / `repo-impact` 的完整调用链

------

## 十、几个我建议你现在就定下来的硬约束

### 1. 不再把“聊天”当产品主入口

CLI 里可以留一个调试壳，但不要再做 `chat` 作为主功能。真正的交互层已经是 Claude Code / Codex。

### 2. 所有能力先做成可组合的小工具

一旦你又开始做“大而全 ask 接口”，旧复杂度会原样回来。

### 3. 所有输出都围绕 evidence 组织

不要回到 whole-repo JSON / markdown export 思维。

### 4. 所有路径都用中性命名

`.codewiki/`，不是 `.claude/`。

### 5. 技能是 procedure，仓库说明是 facts

Claude Code 官方文档对这点讲得很清楚：当一段说明已经变成可复用流程，就该拆进 skill，而不是继续塞在 `CLAUDE.md` 里。

------

## 最后给你一个明确结论

你的新项目不应该是“mycodewiki 的 2.0 重构版”，而应该是：

**一个新的、轻内核、强边界、面向 MCP 和 Skills 的本地代码分析平台。**

旧仓库的角色应该降级为三件事：

- **规范来源**：用它的 active spec 定义边界；
- **测试来源**：把 fixtures/tests 迁进新仓；
- **低层代码来源**：只挑 tree-sitter、scope heuristics、少量 export helper、少量 FSoft C 模块来吸收。

而不再是“主线代码基础”。

下一步最值得做的是：**把这份方案继续收敛成“新仓库初始化清单 + 逐目录职责说明 + 首批 9 个 MCP tools 的 JSON contract 草案”**。