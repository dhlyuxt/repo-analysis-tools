user:我认为当前的mcp设计很烂，原因在于它用自然语言作为输入，而且承担了太多语义层的功能。这导致agent给mcp的输入模糊不清，而mcp又天然对模糊不清的输入难以有效响应。你是否同意这个判断。如果同意，我该怎么改



同意，而且我会说得更重一点：**你当前 MCP 的主要问题不是“工具实现还不够聪明”，而是“把本该由 agent/skill 处理的语义理解职责，下沉到了 MCP 工具里”**。

更精确地说：

> 自然语言可以出现在最外层，但不应该成为核心分析工具的主要输入。
>  MCP 的核心工具应该像数据库查询器、索引查询器、图查询器、证据读取器，而不是“仓库理解问答器”。

你现在的设计里，`plan_slice(target_repo, question)` 是最典型的问题点。contract 里它的输入就是 `target_repo` 和 `question`，输出是 `query_kind/status/selected_files/selected_anchor_names/notes`；同时 skill 又要求把它放在主流程中间，用它把问题转成 slice。 但代码里的 `QueryClassifier` 只识别少数英文模式，例如 “where is X defined?”、“what is the role of X?”、以及 `startup/init flow` 这类英文关键词，其他都落到 `general_question`。 这就必然导致你说的现象：agent 给 MCP 的输入模糊，MCP 又没有足够上下文和语义能力，最后只能返回不好用的结果。

MCP 规范本身并不要求工具吃自然语言。官方 MCP tool 定义里强调的是工具名、描述、`inputSchema`、可选 `outputSchema`；结构化输出还可以帮助客户端和 LLM 正确解析、验证和使用结果。 所以问题不在 MCP，而在你的工具边界设计。

------

## 我的判断

你现在的 MCP 设计混合了三层职责：

```
用户意图理解层：用户到底想问什么？
分析规划层：应该查 symbol、file、call graph、module，还是 impact？
确定性查询层：给定 scan_id/entity_id/path/span，返回索引、关系、证据。
```

现在 `plan_slice(question)` 把这三层揉在一起了。

结果就是：

```
用户中文问题
  ↓
agent 不稳定地改写成某个英文/中文 question
  ↓
plan_slice 尝试分类
  ↓
分类失败或弱匹配
  ↓
slice 质量差
  ↓
evidence pack 质量差
  ↓
最终回答也差
```

正确方向应该是：

```
用户自然语言
  ↓
agent/skill 做语义拆解
  ↓
MCP 只接收结构化 selector / entity id / graph query / slice spec
  ↓
MCP 返回确定性索引结果、候选、证据和诊断
  ↓
agent 组织回答
```

也就是说，**MCP 不应该“理解问题”，它应该“执行明确查询”**。

------

## 核心改法：把 MCP 从“语义工具”改成“代码索引查询 API”

你可以把新的工具分成三层。

### 第一层：索引与状态工具

这些工具只负责建立和读取分析资产，不承担语义解释。

```
scan_repo
get_scan_status
build_code_index
get_index_status
get_index_diagnostics
```

其中 `build_code_index` 应该输出稳定索引 ID：

```
{
  "index_id": "index_abc123",
  "scan_id": "scan_def456",
  "languages": ["c", "h"],
  "files_indexed": 318,
  "symbols_indexed": 2741,
  "relations_indexed": 8012,
  "diagnostics": {
    "parser_backend": {
      "tree_sitter": 287,
      "regex_fallback": 31
    },
    "skipped_files": [],
    "ambiguous_symbols": 42,
    "unresolved_calls": 319
  }
}
```

这里不需要问“你想了解什么”。它只是建立事实库。

------

### 第二层：确定性查询工具

这是最重要的改造。把现在的 `list_anchors/find_anchor/describe_anchor/plan_slice` 拆成一组强类型查询工具。

#### 1. `search_entities`

替代现在偏模糊的 `find_anchor(anchor_name)`。

```
{
  "index_id": "index_abc123",
  "name": "foo_init",
  "kinds": ["function"],
  "match": "exact",
  "path_globs": ["src/**/*.c", "include/**/*.h"],
  "limit": 20
}
```

输出：

```
{
  "status": "ok",
  "matches": [
    {
      "entity_id": "ent_001",
      "kind": "function",
      "name": "foo_init",
      "qualified_name": "src/foo.c::foo_init",
      "path": "src/foo.c",
      "line_start": 42,
      "line_end": 89,
      "is_definition": true,
      "confidence": "high"
    }
  ],
  "ambiguity": null
}
```

关键点：**返回 `entity_id`，后续所有工具都用 ID，不再用裸字符串名字。**

------

#### 2. `resolve_entity`

用于处理同名函数、static 函数、多平台实现、声明/定义分离。

```
{
  "index_id": "index_abc123",
  "selector": {
    "name": "init",
    "kind": "function",
    "path_hint": "src/net"
  },
  "resolution_policy": "return_candidates"
}
```

如果不唯一，不要猜：

```
{
  "status": "ambiguous",
  "candidates": [
    {
      "entity_id": "ent_101",
      "name": "init",
      "path": "src/net/init.c",
      "why": "path matches hint src/net"
    },
    {
      "entity_id": "ent_102",
      "name": "init",
      "path": "src/fs/init.c",
      "why": "same name, different module"
    }
  ],
  "next_action": {
    "tool": "get_entity",
    "args_template": {
      "entity_id": "<candidate.entity_id>"
    }
  }
}
```

这比 `describe_anchor(anchor_name)` 靠谱得多。

------

#### 3. `get_entity`

给定实体 ID，返回实体事实。

```
{
  "entity_id": "ent_001",
  "include": [
    "signature",
    "definition_span",
    "declarations",
    "doc_comment",
    "callers",
    "callees",
    "related_types",
    "related_macros"
  ]
}
```

输出应该是 answer-ready 的结构化事实，但不要写自然语言长文：

```
{
  "entity": {
    "entity_id": "ent_001",
    "kind": "function",
    "name": "foo_init",
    "path": "src/foo.c",
    "line_start": 42,
    "line_end": 89,
    "signature": "int foo_init(struct foo_ctx *ctx)"
  },
  "callers": [
    {
      "entity_id": "ent_200",
      "name": "main",
      "path": "src/main.c",
      "call_site": {
        "path": "src/main.c",
        "line": 77
      }
    }
  ],
  "callees": [
    {
      "entity_id": "ent_301",
      "name": "foo_alloc",
      "path": "src/foo_alloc.c"
    }
  ],
  "citations": [
    {
      "citation_id": "cit_001",
      "path": "src/foo.c",
      "line_start": 42,
      "line_end": 89
    }
  ],
  "diagnostics": {
    "has_unresolved_calls": true,
    "unresolved_call_names": ["BAR_CALL"]
  }
}
```

------

#### 4. `query_relations`

替代一堆“谁调用谁”的隐式逻辑。

```
{
  "index_id": "index_abc123",
  "seed_entity_ids": ["ent_001"],
  "direction": "both",
  "relation_kinds": [
    "direct_call",
    "macro_expansion",
    "declaration_of",
    "type_reference",
    "include"
  ],
  "depth": 2,
  "max_nodes": 100
}
```

输出：

```
{
  "nodes": [...],
  "edges": [
    {
      "source": "ent_200",
      "target": "ent_001",
      "kind": "direct_call",
      "evidence": {
        "path": "src/main.c",
        "line": 77
      },
      "confidence": "high"
    }
  ],
  "blind_spots": [
    {
      "kind": "function_pointer_call",
      "path": "src/foo.c",
      "line": 63,
      "reason": "callee is member_expression, not statically resolved"
    }
  ]
}
```

这个工具是 C 仓库阅读里非常核心的工具。它应该是确定性的图查询，而不是自然语言问答。

------

#### 5. `build_slice`

替代 `plan_slice(target_repo, question)`。

当前 `plan_slice` 的最大问题是“给它一句话，让它自己猜 slice”。你应该改成“给它明确 seeds 和 expansion policy”。

```
{
  "index_id": "index_abc123",
  "seeds": {
    "entity_ids": ["ent_001"],
    "paths": ["src/foo.c"]
  },
  "expansion": {
    "include_callers": true,
    "include_callees": true,
    "include_declarations": true,
    "include_headers": true,
    "relation_depth": 2
  },
  "budget": {
    "max_files": 12,
    "max_entities": 80,
    "max_lines": 1200
  }
}
```

输出：

```
{
  "slice_id": "slice_abc123",
  "selected_files": [...],
  "selected_entities": [...],
  "excluded_due_to_budget": [...],
  "coverage": {
    "callers_included": 8,
    "callees_included": 14,
    "headers_included": 3,
    "unresolved_edges": 6
  }
}
```

这样 MCP 的行为就可预测了。

------

#### 6. `build_evidence_pack`

这个可以保留，但输入应来自明确 slice，不来自自然语言。

```
{
  "slice_id": "slice_abc123",
  "citation_policy": {
    "include_entity_definitions": true,
    "include_call_sites": true,
    "include_declarations": true,
    "max_span_lines": 80
  }
}
```

输出不仅要有 citations，还应该有 facts：

```
{
  "evidence_pack_id": "ev_001",
  "facts": [
    {
      "fact_id": "fact_001",
      "claim_type": "call_relation",
      "subject": "main",
      "predicate": "calls",
      "object": "foo_init",
      "confidence": "high",
      "citations": ["cit_010"]
    }
  ],
  "citations": [...]
}
```

------

#### 7. `open_citation`

替代现在的 `open_span(target_repo, evidence_pack_id, path, line_start, line_end)`。

你现在让 agent 传 path + line range，agent 很容易传错。更好的是只允许：

```
{
  "citation_id": "cit_010"
}
```

或者最多：

```
{
  "citation_id": "cit_010",
  "window": {
    "before": 5,
    "after": 5
  }
}
```

这样 agent 不需要拼路径和行号，也不会越界。

------

## 自然语言应该放在哪里？

不是完全删掉自然语言，而是只能放在两个地方之一。

### 方案 A：完全交给 agent/skill

用户问：

```
这个仓库启动流程在哪里？
```

skill 指导 agent 做：

```
1. scan_repo / build_code_index
2. search_entities(name="main", kinds=["function"])
3. search_entities(name="*_init", kinds=["function"], match="glob")
4. query_relations(seed_entity_ids=[main], direction="out", depth=3)
5. build_slice(...)
6. build_evidence_pack(...)
```

MCP 不接收“这个仓库启动流程在哪里？”这句话。

这个方案最干净。

------

### 方案 B：保留一个很薄的语义编译工具

如果你确实想让 MCP 帮忙做一点 routing，可以保留一个工具，但它不能直接做分析。

名字不要叫 `plan_slice`，而叫：

```
compile_repo_question
```

输入可以是自然语言：

```
{
  "question": "这个仓库启动流程在哪里？",
  "language": "zh-CN"
}
```

但输出必须是结构化计划，而不是 slice：

```
{
  "intent": "trace_initialization_flow",
  "confidence": "medium",
  "required_queries": [
    {
      "tool": "search_entities",
      "args": {
        "name": "main",
        "kinds": ["function"],
        "match": "exact"
      }
    },
    {
      "tool": "search_entities",
      "args": {
        "name": "*init*",
        "kinds": ["function"],
        "match": "glob"
      }
    }
  ],
  "ambiguities": [
    "init flow may mean program startup, driver init, module init, or bootloader init"
  ]
}
```

也就是说，语义工具只能做“编译意图”，不能直接做“分析结论”。

我更推荐方案 A；如果担心不同 agent 表现不稳定，再加方案 B。

------

## 新的 MCP 设计原则

我建议你按这几条重构。

### 1. MCP 工具输入必须是 typed selector，不是 full question

坏：

```
{
  "question": "帮我看看这个模块是干嘛的"
}
```

好：

```
{
  "module_id": "mod_net",
  "include": ["public_api", "entrypoints", "dependencies", "key_files"]
}
```

坏：

```
{
  "anchor_name": "init"
}
```

好：

```
{
  "entity_id": "ent_123"
}
```

或者：

```
{
  "selector": {
    "name": "init",
    "kind": "function",
    "path_glob": "src/net/**"
  },
  "on_ambiguous": "return_candidates"
}
```

------

### 2. 所有模糊性都显式返回，不要在 MCP 内部猜

例如：

```
{
  "status": "ambiguous",
  "candidates": [...],
  "reason": "5 functions named init found",
  "recommended_disambiguators": [
    "path_glob",
    "kind",
    "module_id",
    "is_definition"
  ]
}
```

不要：

```
{
  "status": "ok",
  "description": "init probably refers to ..."
}
```

------

### 3. 所有后续调用都基于稳定 ID

应该逐步用这些 ID 串起来：

```
repo_id
scan_id
index_id
module_id
entity_id
relation_id
slice_id
evidence_pack_id
citation_id
report_id
```

不要让 agent 在后续调用里反复传：

```
anchor_name
path + line_start + line_end
question
module_name
```

这些都容易变形、歧义或失配。

------

### 4. MCP 返回“事实”和“诊断”，不要返回大段解释

MCP 返回：

```
{
  "facts": [...],
  "relations": [...],
  "citations": [...],
  "diagnostics": [...]
}
```

agent 负责把这些组织成：

```
这个模块主要负责 ...
入口函数是 ...
初始化路径是 ...
不确定点是 ...
```

这样分层更清晰。

------

### 5. 工具不要太多，但每个工具要是正交能力

你当前 README 里写到有 8 个 tool domain、24 个工具，并且主流程是 `scan -> scope -> anchors -> slice -> evidence -> impact -> report -> export`。 这个流程从工程管线角度能理解，但对 agent 来说太像“内部步骤”。你可以把 agent-facing 工具减少到 10 个左右：

```
ensure_index
get_index_status
search_entities
resolve_entity
get_entity
query_relations
list_modules
get_module
build_slice
build_evidence_pack
open_citation
```

impact/report/export 可以先作为高级工具保留：

```
analyze_impact
render_report
export_bundle
```

但不要让普通 repo understanding 一上来就暴露 24 个工具给 agent 选择。

------

## 我会怎么具体改你的现有工具

### 现有 `plan_slice(target_repo, question)`

建议废弃，改成：

```
build_slice(index_id, seeds, expansion, budget)
```

旧工具暂时保留为：

```
legacy_plan_slice
```

并在描述里明确：

```
Deprecated. Do not use for new workflows. Use search_entities + build_slice instead.
```

------

### 现有 `find_anchor(target_repo, scan_id, anchor_name)`

改成：

```
search_entities(index_id, name, kinds, match, path_globs, limit)
```

原因：`anchor_name` 太弱，无法表达 kind、路径、是否定义、匹配策略。

------

### 现有 `describe_anchor(target_repo, scan_id, anchor_name)`

改成：

```
get_entity(entity_id, include)
```

原因：`anchor_name` 不稳定。同名 static 函数、宏、类型、声明/定义都会冲突。

------

### 现有 `list_anchors`

保留，但降级为 debug 工具。

更好的日常入口是：

```
search_entities
list_modules
get_file_outline
```

------

### 现有 `show_scope/list_scope_nodes/explain_scope_node`

改成更明确的模块模型：

```
list_modules(index_id, filters)
get_module(module_id, include)
```

`scope node` 这个名字偏内部，agent 不一定知道它和“模块”“目录”“组件”的关系。`module` 更贴近用户问题。

------

### 现有 `open_span`

改成：

```
open_citation(citation_id)
```

或者：

```
open_entity_definition(entity_id)
open_relation_evidence(relation_id)
```

不要再让 agent 手动传 line range。

------

## 推荐的新 contract 草案

你可以把 contract 改成这种形式。

```
index
  ensure_index(target_repo, policy)
  get_index_status(index_id)
  get_index_diagnostics(index_id)

entity
  search_entities(index_id, name?, tokens?, kinds?, match?, path_globs?, limit?)
  resolve_entity(index_id, selector, resolution_policy)
  get_entity(entity_id, include?)

module
  list_modules(index_id, filters?)
  get_module(module_id, include?)

graph
  query_relations(index_id, seed_entity_ids, direction, relation_kinds, depth, filters?, budget?)

slice
  build_slice(index_id, seeds, expansion, budget)
  get_slice(slice_id)

evidence
  build_evidence_pack(slice_id, citation_policy)
  read_evidence_pack(evidence_pack_id)
  open_citation(citation_id)

impact
  analyze_impact(index_id, seeds, propagation_policy, budget)

report
  render_report(evidence_pack_id, report_spec)
```

这里面只有 `search_entities` 允许一点字符串输入，但它的字符串是“名字/模式/关键词”，不是自然语言任务。

------

## skill 也要跟着改

你现在的 skill 是固定顺序：

```
scan_repo -> get_scan_status -> show_scope -> list_anchors/find_anchor/describe_anchor -> plan_slice -> build_evidence_pack -> read_evidence_pack -> open_span
```

这个顺序本身就鼓励 agent 把自然语言丢给 `plan_slice`。

建议改成“意图到结构化查询”的规则。

例如：

```
## Do not send the user's full natural-language question to MCP analysis tools.

For repository understanding:
1. ensure_index
2. classify the user's request yourself
3. call typed query tools:
   - symbol question -> search_entities -> resolve_entity -> get_entity
   - call flow question -> search_entities -> query_relations
   - module question -> list_modules -> get_module
   - impact question -> analyze_impact
4. build_slice only from explicit seeds
5. build_evidence_pack
6. open_citation only by citation_id
```

再加几个例子。

### 例子一：用户问“foo_init 是干嘛的？”

```
search_entities(name="foo_init", kinds=["function"], match="exact")
resolve_entity(...)
get_entity(entity_id, include=["signature", "callers", "callees", "definition_span"])
build_slice(seeds={"entity_ids": [...]}, expansion={...})
build_evidence_pack(slice_id)
open_citation(citation_id)
```

### 例子二：用户问“启动流程在哪里？”

```
search_entities(name="main", kinds=["function"], match="exact")
search_entities(name="*init*", kinds=["function"], match="glob")
query_relations(seed_entity_ids=[main_entity], direction="out", depth=3)
build_slice(...)
build_evidence_pack(...)
```

### 例子三：用户问“改 src/net/socket.c 会影响哪里？”

```
search_entities(path_globs=["src/net/socket.c"])
query_relations(seed_entity_ids=[entities_in_file], direction="in", depth=2)
analyze_impact(...)
```

------

## 你可以分三阶段改

### 第一阶段：马上降低未命中率

不大改内部实现，只改接口。

1. 新增 `search_entities`，内部先复用现有 anchors。
2. 新增 `get_entity(entity_id)`，内部映射到现有 anchor。
3. 新增 `build_slice_from_seeds`，内部复用现有 slice service。
4. 新增 `open_citation(citation_id)`，内部复用 evidence pack。
5. 把 `plan_slice(question)` 标成 deprecated。
6. skill 中禁止把用户原问题传给 `plan_slice`。

这一阶段做完，agent 未命中会明显减少。

------

### 第二阶段：把 anchor 名称体系改成实体 ID 体系

现在很多工具围绕 `anchor_name` 工作，这对 C 仓库很危险。

你需要引入：

```
entity_id = hash(kind + normalized_name + path + line_start + line_end + definition/declaration)
```

然后所有关系都用：

```
source_entity_id
target_entity_id
relation_kind
evidence_span
confidence
resolution_status
```

尤其要支持：

```
resolved
unresolved
ambiguous
external
macro_like
function_pointer_like
```

不要把解析不了的边丢掉。C 仓库里“解析不了的边”本身就是重要诊断。

------

### 第三阶段：重建 module/scope

把现在的 scope 从目录启发式升级成模块索引。

模块可以由多种证据合并出来：

```
目录聚类
header/source pairing
include graph
build target
Kconfig/CMake/Makefile
public headers
entrypoint symbols
```

模块输出应该是：

```
{
  "module_id": "mod_net",
  "name": "net",
  "root_paths": ["src/net", "include/net"],
  "public_headers": ["include/net/*.h"],
  "implementation_files": ["src/net/*.c"],
  "entrypoints": ["net_init", "socket_create"],
  "depends_on": ["mod_core", "mod_hal"],
  "confidence": "medium",
  "why": [
    "header/source pairing",
    "include graph cluster",
    "path prefix"
  ]
}
```

这样用户问“这个模块做什么”，agent 就可以调用 `get_module(module_id)`，而不是把“这个模块做什么”传给 MCP。

------

## 一句话架构建议

你应该把项目从：

```
MCP = 语义理解 + 代码分析 + 证据构造
```

改成：

```
Agent/Skill = 语义理解和任务拆解
MCP = 类型化代码索引查询、图查询、证据读取
```

再浓缩一点：

> MCP 工具不要回答“用户想问什么”；MCP 工具只回答“给定这些 ID、selector、relation query，代码索引里有什么事实”。

这会让工具更笨、更窄、更稳定，但整体系统会更聪明。