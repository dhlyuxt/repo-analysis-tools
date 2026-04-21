# M7 Minimal Query MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current MCP surface with the nine-tool minimal query surface defined in the 2026-04-20 design/spec docs, with the old MCP interfaces physically removed from the active tree.

**Architecture:** Build the new surface on top of the existing scan, anchor, and scope stores instead of inventing a second persistence model. Reorder scan rebuilds so anchor data is available before scope file-fact aggregation, add a dedicated query service for file/symbol/graph lookups, and add a process-local `scan_id -> repo_root` registry so wrappers can honor the no-`target_repo` query contracts. Old MCP interfaces are removed from registration, active docs, active skills, active demos, and active tests; this plan intentionally overrides the earlier M7 note about keeping legacy tools around.

**Tech Stack:** Python 3.11, FastMCP, `tree-sitter-c`, stdlib `unittest`, `/home/hyx/anaconda3/envs/agent/bin/python -m pytest`

---

## File Structure

### New Files

- Create: `src/repo_analysis_tools/query/__init__.py`
  Responsibility: package entry for the new query domain.
- Create: `src/repo_analysis_tools/query/models.py`
  Responsibility: typed records for file-priority rows, file-info rows, symbol rows, call relation rows, and call-path rows.
- Create: `src/repo_analysis_tools/query/path_search.py`
  Responsibility: bounded simple-path enumeration for `find_call_paths`.
- Create: `src/repo_analysis_tools/query/service.py`
  Responsibility: pure query orchestration over persisted scan/anchor/scope assets.
- Create: `src/repo_analysis_tools/mcp/contracts/query.py`
  Responsibility: contract declarations for the eight non-scan query tools.
- Create: `src/repo_analysis_tools/mcp/scan_registry.py`
  Responsibility: process-local `scan_id -> repo_root` lookup used by `rebuild_repo_snapshot` and all query wrappers.
- Create: `src/repo_analysis_tools/mcp/tools/query_tools.py`
  Responsibility: FastMCP wrappers for the eight non-scan query tools.
- Create: `tests/fixtures/query_repo.py`
  Responsibility: deterministic fixture for file-priority, symbol lookup, and symbol-context tests.
- Create: `tests/fixtures/query_path_repo.py`
  Responsibility: deterministic fixture for multi-path and truncation path tests.
- Create: `tests/unit/test_query_service.py`
  Responsibility: unit coverage for the new query service.
- Create: `tests/integration/test_minimal_query_workflow.py`
  Responsibility: end-to-end workflow coverage for the new nine-tool query surface.

### Modified Files

- Modify: `src/repo_analysis_tools/scan/service.py`
  Responsibility: rename runtime-facing rebuild path to `rebuild_repo_snapshot` behavior and rebuild anchors before scope.
- Modify: `src/repo_analysis_tools/scope/models.py`
  Responsibility: persist file-level facts needed by `list_priority_files` and `get_file_info`.
- Modify: `src/repo_analysis_tools/scope/service.py`
  Responsibility: compute persisted file facts, `priority_score`, and file-level counters from scan + anchor data.
- Modify: `src/repo_analysis_tools/mcp/contracts/scan.py`
  Responsibility: collapse the scan surface to one contract: `rebuild_repo_snapshot`.
- Modify: `src/repo_analysis_tools/mcp/contracts/__init__.py`
  Responsibility: register only the new scan + query contract sets.
- Modify: `src/repo_analysis_tools/mcp/tools/scan_tools.py`
  Responsibility: expose only `rebuild_repo_snapshot` and remember returned `scan_id` values in the runtime registry.
- Modify: `src/repo_analysis_tools/mcp/tools/__init__.py`
  Responsibility: register only `scan_tools` and `query_tools` with the server.
- Modify: `tests/unit/test_scope_service.py`
  Responsibility: assert enriched persisted file facts and new scan ordering.
- Modify: `tests/unit/test_scan_service.py`
  Responsibility: assert rebuild output shape and enriched scope persistence.
- Modify: `tests/contract/test_tool_contracts.py`
  Responsibility: rewrite contract assertions around the new nine-tool surface.
- Modify: `tests/smoke/test_mcp_server.py`
  Responsibility: assert only the new surface is registered.
- Modify: `tests/smoke/test_package_layout.py`
  Responsibility: assert the legacy MCP wrapper/contract files and obsolete skills/tests are gone from the active tree.
- Modify: `tests/unit/test_architecture_docs.py`
  Responsibility: assert active architecture docs no longer reference the removed interfaces.
- Modify: `tests/unit/test_client_skill_distribution.py`
  Responsibility: assert only the remaining active skill is mirrored between `.agents/skills` and `.claude/skills`.
- Modify: `tests/unit/test_launch_docs.py`
  Responsibility: assert active launch docs and README describe only the new workflow and demo command.
- Modify: `README.md`
  Responsibility: describe the new active tool surface and remove old workflow descriptions.
- Modify: `docs/contracts/mcp-tool-contracts.md`
  Responsibility: publish the new contract surface only.
- Modify: `docs/architecture.md`
  Responsibility: describe the new query-first mainline.
- Modify: `docs/self-use-launch.md`
  Responsibility: replace old operational guidance with the new surface.
- Modify: `.agents/skills/repo-understand/SKILL.md`
  Responsibility: align the active repository-reading skill with the new surface.
- Modify: `.claude/skills/repo-understand/SKILL.md`
  Responsibility: keep the mirrored Claude skill identical to the active agent skill.
- Modify: `tools/run_self_use_demo.py`
  Responsibility: exercise only the new query-first workflow and emit a minimal structured demo summary.
- Modify: `tests/integration/test_self_use_demo.py`
  Responsibility: validate the rewritten self-use demo output.

### Required Manual Purge Commands (User-Run Only)

Because this repository forbids assistant-driven delete operations, these removals must be run manually by a human during implementation after the replacement suite is green. The final active tree should no longer contain any of these interface files or workflow tests:

```bash
rm src/repo_analysis_tools/mcp/contracts/anchors.py
rm src/repo_analysis_tools/mcp/contracts/evidence.py
rm src/repo_analysis_tools/mcp/contracts/export.py
rm src/repo_analysis_tools/mcp/contracts/impact.py
rm src/repo_analysis_tools/mcp/contracts/report.py
rm src/repo_analysis_tools/mcp/contracts/scope.py
rm src/repo_analysis_tools/mcp/contracts/slice.py
rm src/repo_analysis_tools/mcp/tools/anchors_tools.py
rm src/repo_analysis_tools/mcp/tools/evidence_tools.py
rm src/repo_analysis_tools/mcp/tools/export_tools.py
rm src/repo_analysis_tools/mcp/tools/impact_tools.py
rm src/repo_analysis_tools/mcp/tools/report_tools.py
rm src/repo_analysis_tools/mcp/tools/scope_tools.py
rm src/repo_analysis_tools/mcp/tools/slice_tools.py
rm .agents/skills/analysis-maintenance/SKILL.md
rm .agents/skills/analysis-writing/SKILL.md
rm .agents/skills/change-impact/SKILL.md
rm .claude/skills/analysis-maintenance/SKILL.md
rm .claude/skills/analysis-writing/SKILL.md
rm .claude/skills/change-impact/SKILL.md
rm tests/integration/test_analysis_writing_workflow.py
rm tests/integration/test_change_impact_workflow.py
rm tests/integration/test_export_reuse_workflow.py
rm tests/integration/test_mainline_mcp_workflow.py
rm tests/e2e/test_analysis_writing_easyflash.py
rm tests/e2e/test_change_impact_easyflash.py
rm tests/e2e/test_export_easyflash.py
rm tests/e2e/test_repo_understand_easyflash.py
rm tests/e2e/test_self_use_launch_easyflash.py
rm tests/golden/test_contract_golden.py
rm tests/golden/fixtures/export_analysis_bundle_scope_first.json
rm tests/golden/fixtures/export_evidence_bundle_scope_first.json
rm tests/golden/fixtures/export_scope_snapshot_scope_first.json
rm tests/golden/fixtures/read_evidence_pack_scope_first.json
rm tests/golden/fixtures/render_module_summary_scope_first.json
rm tests/golden/fixtures/scan_repo.json
rm tests/golden/fixtures/summarize_impact_scope_first.json
```

If you prefer archive-over-delete, move those files under a new history directory before removing them from active imports and active test discovery.

### Score Formula To Implement

Persist `priority_score` with a deterministic formula so tests can assert ordering without NLP:

```python
ROLE_WEIGHT = {
    "primary": 40,
    "support": 20,
    "external": 5,
    "generated": 0,
}

def compute_priority_score(
    *,
    role: str,
    has_main_definition: bool,
    root_function_count: int,
    function_count: int,
    incoming_call_count: int,
    outgoing_call_count: int,
) -> int:
    score = ROLE_WEIGHT[role]
    if has_main_definition:
        score += 50
    score += min(root_function_count * 15, 30)
    score += min(function_count * 2, 20)
    score += min(incoming_call_count, 20)
    score += min(outgoing_call_count, 20)
    return score
```

---

### Task 1: Persist Scope File Facts And Reorder Rebuilds

**Files:**
- Modify: `src/repo_analysis_tools/scope/models.py`
- Modify: `src/repo_analysis_tools/scope/service.py`
- Modify: `src/repo_analysis_tools/scan/service.py`
- Test: `tests/unit/test_scope_service.py`
- Test: `tests/unit/test_scan_service.py`

- [ ] **Step 1: Write the failing tests for enriched scope files**

```python
# tests/unit/test_scope_service.py
    def test_build_snapshot_persists_enriched_file_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)

            snapshot = ScopeService().build_snapshot(repo, scan_snapshot.scan_id)
            by_path = {scoped_file.path: scoped_file for scoped_file in snapshot.files}

            self.assertEqual(by_path["src/main.c"].role, "primary")
            self.assertTrue(by_path["src/main.c"].has_main_definition)
            self.assertEqual(by_path["src/main.c"].function_count, 2)
            self.assertEqual(by_path["src/main.c"].incoming_call_count, 0)
            self.assertEqual(by_path["src/main.c"].outgoing_call_count, 1)
            self.assertEqual(by_path["src/main.c"].root_function_count, 1)
            self.assertGreater(by_path["src/main.c"].priority_score, by_path["src/flash.c"].priority_score)
            self.assertGreater(by_path["src/flash.c"].priority_score, by_path["demo/demo_main.c"].priority_score)

# tests/unit/test_scan_service.py
    def test_scan_service_builds_anchor_snapshot_before_scope_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))

            result = ScanService().scan(repo)
            scope_snapshot = ScopeStore.for_repo(repo).load(result.scan_id)
            by_path = {scoped_file.path: scoped_file for scoped_file in scope_snapshot.files}

            self.assertEqual(by_path["src/flash.c"].incoming_call_count, 2)
            self.assertEqual(by_path["src/flash.c"].root_function_count, 0)
            self.assertEqual(by_path["src/config.h"].macro_count, 1)
```

- [ ] **Step 2: Run the scope and scan tests to verify they fail**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_scope_service.py tests/unit/test_scan_service.py -q
```

Expected:

- FAIL with `AttributeError` or field mismatch for missing `priority_score`, `function_count`, `incoming_call_count`, and related enriched scope fields

- [ ] **Step 3: Implement persisted file facts and rebuild ordering**

```python
# src/repo_analysis_tools/scope/models.py
@dataclass(frozen=True)
class ScopedFile:
    path: str
    role: str
    node_id: str
    priority_score: int
    line_count: int
    symbol_count: int
    function_count: int
    type_count: int
    macro_count: int
    include_count: int
    incoming_call_count: int
    outgoing_call_count: int
    root_function_count: int
    has_main_definition: bool
```

```python
# src/repo_analysis_tools/scope/service.py
from repo_analysis_tools.anchors.store import AnchorStore

ROLE_WEIGHT = {
    "primary": 40,
    "support": 20,
    "external": 5,
    "generated": 0,
}

def _priority_score(
    *,
    role: str,
    has_main_definition: bool,
    root_function_count: int,
    function_count: int,
    incoming_call_count: int,
    outgoing_call_count: int,
) -> int:
    score = ROLE_WEIGHT[role]
    if has_main_definition:
        score += 50
    score += min(root_function_count * 15, 30)
    score += min(function_count * 2, 20)
    score += min(incoming_call_count, 20)
    score += min(outgoing_call_count, 20)
    return score

def build_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> ScopeSnapshot:
    repo = Path(target_repo).expanduser().resolve()
    scan_snapshot = ScanStore.for_repo(repo).load(scan_id=scan_id)
    anchor_snapshot = AnchorStore.for_repo(repo).load(scan_id=scan_snapshot.scan_id)
    config = self.config_loader.load(str(repo))
    scoped_files = self._classify_files(repo, scan_snapshot.files, anchor_snapshot, config)
    nodes = self._build_nodes(scoped_files)
    snapshot = ScopeSnapshot(
        scan_id=scan_snapshot.scan_id,
        files=scoped_files,
        nodes=nodes,
    )
    ScopeStore.for_repo(repo).save(snapshot)
    return snapshot
```

```python
# src/repo_analysis_tools/scan/service.py
    def scan(self, target_repo: Path | str) -> ScanSnapshot:
        repo = Path(target_repo).expanduser().resolve()
        snapshot = self._scan_repo(repo)
        ScanStore.for_repo(repo).save(snapshot)
        AnchorService().build_snapshot(repo, snapshot.scan_id)
        ScopeService().build_snapshot(repo, snapshot.scan_id)
        return snapshot
```

- [ ] **Step 4: Run the scope and scan tests to verify they pass**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_scope_service.py tests/unit/test_scan_service.py -q
```

Expected:

- PASS with all scope and scan assertions green

- [ ] **Step 5: Commit the persisted scope-facts groundwork**

```bash
git add src/repo_analysis_tools/scope/models.py src/repo_analysis_tools/scope/service.py src/repo_analysis_tools/scan/service.py tests/unit/test_scope_service.py tests/unit/test_scan_service.py
git commit -m "feat: persist scope file facts for query mcp"
```

### Task 2: Add Query Fixtures And File/Symbol Query Service

**Files:**
- Create: `src/repo_analysis_tools/query/__init__.py`
- Create: `src/repo_analysis_tools/query/models.py`
- Create: `src/repo_analysis_tools/query/service.py`
- Create: `tests/fixtures/query_repo.py`
- Create: `tests/unit/test_query_service.py`

- [ ] **Step 1: Write the failing tests for file and symbol queries**

```python
# tests/fixtures/query_repo.py
def build_query_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "query-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "include").mkdir(parents=True, exist_ok=True)
    (repo / "ports").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "main.c").write_text(
        '#include "types.h"\n'
        "int flash_init(void);\n"
        "int main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "flash.c").write_text(
        "/* flash init comment */\n"
        "static int helper(void) { return 1; }\n"
        "int flash_init(void) {\n"
        "    return helper();\n"
        "}\n",
        encoding="utf-8",
    )
    (repo / "include" / "types.h").write_text(
        "typedef struct flash_cfg {\n"
        "    int enabled;\n"
        "} flash_cfg;\n",
        encoding="utf-8",
    )
    return repo

# tests/unit/test_query_service.py
class QueryServiceTest(unittest.TestCase):
    def test_file_queries_and_symbol_queries_return_structured_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            priority_files = service.list_priority_files(repo, scan_snapshot.scan_id)
            file_info = service.get_file_info(repo, scan_snapshot.scan_id, "src/main.c")
            file_symbols = service.list_file_symbols(repo, scan_snapshot.scan_id, ["src/main.c", "src/flash.c"])
            file_symbol_map = {row.path: row.symbols for row in file_symbols}
            symbol_matches = service.resolve_symbols(repo, scan_snapshot.scan_id, "flash_init")
            symbol_id = symbol_matches.matches[0].symbol_id
            symbol_context = service.open_symbol_context(repo, scan_snapshot.scan_id, symbol_id, 1)

            self.assertEqual(priority_files[0].path, "src/main.c")
            self.assertEqual(file_info.path, "src/main.c")
            self.assertTrue(file_info.has_main_definition)
            self.assertEqual(symbol_matches.match_count, 1)
            self.assertEqual(symbol_matches.matches[0].kind, "function")
            self.assertEqual(symbol_context.definition_line_start, 2)
            self.assertIn("flash init comment", "\n".join(symbol_context.lines))
            self.assertEqual({symbol.name for symbol in file_symbol_map["src/flash.c"]}, {"flash_init", "helper"})
```

- [ ] **Step 2: Run the query-service test to verify it fails**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_query_service.py -q
```

Expected:

- FAIL with `ModuleNotFoundError: No module named 'repo_analysis_tools.query'`

- [ ] **Step 3: Implement file/symbol query models and service methods**

```python
# src/repo_analysis_tools/query/models.py
@dataclass(frozen=True)
class PriorityFileRow:
    path: str
    priority_score: int

@dataclass(frozen=True)
class FileInfoRow:
    path: str
    role: str
    priority_score: int
    line_count: int
    symbol_count: int
    function_count: int
    type_count: int
    macro_count: int
    include_count: int
    incoming_call_count: int
    outgoing_call_count: int
    root_function_count: int
    has_main_definition: bool

@dataclass(frozen=True)
class SymbolRow:
    symbol_id: str
    name: str
    kind: str
    path: str
    line_start: int
    line_end: int
    is_definition: bool
    storage: str

@dataclass(frozen=True)
class FileSymbolsRow:
    path: str
    symbols: tuple[SymbolRow, ...]

@dataclass(frozen=True)
class SymbolMatchResult:
    match_count: int
    matches: tuple[SymbolRow, ...]

@dataclass(frozen=True)
class SymbolContextRow:
    symbol_id: str
    name: str
    kind: str
    path: str
    definition_line_start: int
    definition_line_end: int
    context_line_start: int
    context_line_end: int
    lines: tuple[str, ...]
```

```python
# src/repo_analysis_tools/query/service.py
class QueryService:
    def _kind_for_anchor(self, anchor_kind: str) -> str:
        if "function" in anchor_kind:
            return "function"
        if anchor_kind.startswith(("struct", "union", "enum", "typedef")):
            return "type"
        if "macro" in anchor_kind:
            return "macro"
        return "variable"

    def _storage_for_anchor(self, anchor) -> str:
        return "static" if getattr(anchor, "is_file_local", False) else "global"

    def _symbol_row(self, anchor) -> SymbolRow:
        return SymbolRow(
            symbol_id=anchor.anchor_id,
            name=anchor.name,
            kind=self._kind_for_anchor(anchor.kind),
            path=anchor.path,
            line_start=anchor.start_line,
            line_end=anchor.end_line,
            is_definition=anchor.kind.endswith("definition"),
            storage=self._storage_for_anchor(anchor),
        )

    def list_priority_files(self, target_repo: Path | str, scan_id: str) -> list[PriorityFileRow]:
        snapshot = ScopeStore.for_repo(target_repo).load(scan_id=scan_id)
        return [
            PriorityFileRow(path=item.path, priority_score=item.priority_score)
            for item in sorted(snapshot.files, key=lambda item: (-item.priority_score, item.path))
        ]

    def get_file_info(self, target_repo: Path | str, scan_id: str, path: str) -> FileInfoRow:
        snapshot = ScopeStore.for_repo(target_repo).load(scan_id=scan_id)
        normalized = normalize_repo_relative_path(Path(target_repo).resolve(), path)
        record = next(item for item in snapshot.files if item.path == normalized)
        return FileInfoRow(
            path=record.path,
            role=record.role,
            priority_score=record.priority_score,
            line_count=record.line_count,
            symbol_count=record.symbol_count,
            function_count=record.function_count,
            type_count=record.type_count,
            macro_count=record.macro_count,
            include_count=record.include_count,
            incoming_call_count=record.incoming_call_count,
            outgoing_call_count=record.outgoing_call_count,
            root_function_count=record.root_function_count,
            has_main_definition=record.has_main_definition,
        )

    def list_file_symbols(self, target_repo: Path | str, scan_id: str, paths: list[str]) -> list[FileSymbolsRow]:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        selected_paths = {normalize_repo_relative_path(Path(target_repo).resolve(), path) for path in paths}
        grouped: dict[str, list[SymbolRow]] = {path: [] for path in selected_paths}
        for anchor in snapshot.anchors:
            if anchor.path in selected_paths:
                grouped.setdefault(anchor.path, []).append(self._symbol_row(anchor))
        return [
            FileSymbolsRow(path=path, symbols=tuple(sorted(symbols, key=lambda item: (item.line_start, item.name, item.symbol_id))))
            for path, symbols in sorted(grouped.items())
        ]

    def resolve_symbols(self, target_repo: Path | str, scan_id: str, symbol_name: str) -> SymbolMatchResult:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        matches = [self._symbol_row(anchor) for anchor in snapshot.anchors if anchor.name == symbol_name]
        ordered = tuple(sorted(matches, key=lambda item: (item.path, item.line_start, item.symbol_id)))
        return SymbolMatchResult(match_count=len(ordered), matches=ordered)

    def open_symbol_context(self, target_repo: Path | str, scan_id: str, symbol_id: str, context_lines: int) -> SymbolContextRow:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        anchor = next(anchor for anchor in snapshot.anchors if anchor.anchor_id == symbol_id)
        source_lines = (Path(target_repo).resolve() / anchor.path).read_text(encoding="utf-8", errors="ignore").splitlines()
        start = max(1, anchor.start_line - context_lines)
        end = min(len(source_lines), anchor.end_line + context_lines)
        return SymbolContextRow(
            symbol_id=anchor.anchor_id,
            name=anchor.name,
            kind=self._kind_for_anchor(anchor.kind),
            path=anchor.path,
            definition_line_start=anchor.start_line,
            definition_line_end=anchor.end_line,
            context_line_start=start,
            context_line_end=end,
            lines=tuple(source_lines[start - 1:end]),
        )
```

- [ ] **Step 4: Run the query-service test to verify it passes**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_query_service.py -q
```

Expected:

- PASS with structured rows returned for priority files, file info, symbol lookup, and symbol context

- [ ] **Step 5: Commit the file/symbol query service**

```bash
git add src/repo_analysis_tools/query/__init__.py src/repo_analysis_tools/query/models.py src/repo_analysis_tools/query/service.py tests/fixtures/query_repo.py tests/unit/test_query_service.py
git commit -m "feat: add file and symbol query service"
```

### Task 3: Implement Graph Queries And Bounded Path Search

**Files:**
- Create: `src/repo_analysis_tools/query/path_search.py`
- Modify: `src/repo_analysis_tools/query/models.py`
- Modify: `src/repo_analysis_tools/query/service.py`
- Create: `tests/fixtures/query_path_repo.py`
- Modify: `tests/unit/test_query_service.py`

- [ ] **Step 1: Write the failing tests for direct graph queries and bounded paths**

```python
# tests/fixtures/query_path_repo.py
def build_query_path_repo(tmp_path: Path, branch_count: int = 2) -> Path:
    repo = tmp_path / "query-path-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    lines = ["int dst(void) { return 0; }"]
    for index in range(branch_count):
        lines.append(f"int mid_{index}(void) {{ return dst(); }}")
    fanout = " + ".join(f"mid_{index}()" for index in range(branch_count)) or "0"
    lines.append(f"int src(void) {{ return {fanout}; }}")
    (repo / "src" / "graph.c").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return repo

# tests/unit/test_query_service.py
    def test_graph_queries_return_direct_relations_roots_and_bounded_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_path_repo(Path(tmpdir), branch_count=10)
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            src_id = service.resolve_symbols(repo, scan_snapshot.scan_id, "src").matches[0].symbol_id
            dst_id = service.resolve_symbols(repo, scan_snapshot.scan_id, "dst").matches[0].symbol_id

            relations = service.query_call_relations(repo, scan_snapshot.scan_id, dst_id)
            roots = service.find_root_functions(repo, scan_snapshot.scan_id, ["src/graph.c"])
            paths = service.find_call_paths(repo, scan_snapshot.scan_id, src_id, dst_id)

            self.assertEqual({row.name for row in relations.callers}, {f"mid_{i}" for i in range(10)})
            self.assertEqual({row.name for row in roots}, {"src"})
            self.assertEqual(paths.status, "truncated")
            self.assertEqual(paths.returned_path_count, 8)
            self.assertEqual(paths.paths[0].hop_count, 2)
            self.assertEqual(paths.paths[0].nodes[0].name, "src")
            self.assertEqual(paths.paths[0].nodes[-1].name, "dst")
```

- [ ] **Step 2: Run the graph-focused query-service tests to verify they fail**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_query_service.py -q
```

Expected:

- FAIL with `AttributeError` for missing `query_call_relations`, `find_root_functions`, or `find_call_paths`

- [ ] **Step 3: Implement direct graph queries and bounded path enumeration**

```python
# src/repo_analysis_tools/query/models.py
@dataclass(frozen=True)
class CallRelationRow:
    symbol_id: str
    name: str
    path: str
    call_lines: tuple[int, ...]

@dataclass(frozen=True)
class NonResolvedCallRow:
    name: str
    status: str
    call_lines: tuple[int, ...]

@dataclass(frozen=True)
class CallRelationResult:
    callers: tuple[CallRelationRow, ...]
    callees: tuple[CallRelationRow, ...]
    non_resolved_callees: tuple[NonResolvedCallRow, ...]

@dataclass(frozen=True)
class PathNodeRow:
    symbol_id: str
    name: str
    path: str

@dataclass(frozen=True)
class CallPathRow:
    hop_count: int
    nodes: tuple[PathNodeRow, ...]
    call_lines: tuple[int, ...]

@dataclass(frozen=True)
class PathSearchResult:
    status: str
    returned_path_count: int
    truncated: bool
    paths: tuple[CallPathRow, ...]
```

```python
# src/repo_analysis_tools/query/path_search.py
def enumerate_simple_paths(
    adjacency: dict[str, list[tuple[str, int]]],
    start: str,
    goal: str,
    *,
    limit: int,
) -> tuple[list[list[tuple[str, int | None]]], bool]:
    queue: deque[list[tuple[str, int | None]]] = deque([[(start, None)]])
    found: list[list[tuple[str, int | None]]] = []
    truncated = False
    while queue and len(found) < limit:
        path = queue.popleft()
        node = path[-1][0]
        if node == goal:
            found.append(path)
            continue
        for next_node, line in adjacency.get(node, []):
            if next_node in {item[0] for item in path}:
                continue
            queue.append(path + [(next_node, line)])
    if queue:
        truncated = True
    return found, truncated
```

```python
# src/repo_analysis_tools/query/service.py
PATH_LIMIT = 8

    def _call_row(self, anchor, line: int | None) -> CallRelationRow:
        return CallRelationRow(
            symbol_id=anchor.anchor_id,
            name=anchor.name,
            path=anchor.path,
            call_lines=((line or 0),),
        )

    def _call_adjacency(self, snapshot) -> dict[str, list[tuple[str, int]]]:
        adjacency: dict[str, list[tuple[str, int]]] = {}
        for relation in snapshot.relations:
            if relation.kind == "direct_call" and relation.target_anchor_id is not None:
                adjacency.setdefault(relation.source_anchor_id, []).append((relation.target_anchor_id, relation.line or 0))
        for edges in adjacency.values():
            edges.sort(key=lambda item: (item[0], item[1]))
        return adjacency

    def query_call_relations(self, target_repo: Path | str, scan_id: str, function_id: str) -> CallRelationResult:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        anchors_by_id = {anchor.anchor_id: anchor for anchor in snapshot.anchors}
        callers = []
        callees = []
        unresolved = []
        for relation in snapshot.relations:
            if relation.kind != "direct_call":
                continue
            if relation.target_anchor_id == function_id:
                caller = anchors_by_id[relation.source_anchor_id]
                callers.append(self._call_row(caller, relation.line))
            elif relation.source_anchor_id == function_id and relation.target_anchor_id is not None:
                callee = anchors_by_id[relation.target_anchor_id]
                callees.append(self._call_row(callee, relation.line))
            elif relation.source_anchor_id == function_id:
                unresolved.append(
                    NonResolvedCallRow(
                        name=relation.target_name,
                        status="unresolved",
                        call_lines=((relation.line or 0),),
                    )
                )
        return CallRelationResult(
            callers=tuple(sorted(callers, key=lambda item: (item.path, item.name, item.symbol_id))),
            callees=tuple(sorted(callees, key=lambda item: (item.path, item.name, item.symbol_id))),
            non_resolved_callees=tuple(sorted(unresolved, key=lambda item: (item.name, item.call_lines))),
        )

    def find_root_functions(self, target_repo: Path | str, scan_id: str, paths: list[str]) -> list[SymbolRow]:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        repo = Path(target_repo).resolve()
        selected_paths = {normalize_repo_relative_path(repo, path) for path in paths}
        called_targets = {relation.target_anchor_id for relation in snapshot.relations if relation.kind == "direct_call" and relation.target_anchor_id}
        return sorted(
            [
            self._symbol_row(anchor)
            for anchor in snapshot.anchors
            if anchor.kind == "function_definition" and anchor.path in selected_paths and anchor.anchor_id not in called_targets
            ],
            key=lambda item: (item.path, item.line_start, item.name, item.symbol_id),
        )

    def find_call_paths(self, target_repo: Path | str, scan_id: str, from_function_id: str, to_function_id: str) -> PathSearchResult:
        snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
        anchors_by_id = {anchor.anchor_id: anchor for anchor in snapshot.anchors}
        adjacency = self._call_adjacency(snapshot)
        raw_paths, truncated = enumerate_simple_paths(adjacency, from_function_id, to_function_id, limit=PATH_LIMIT)
        paths = []
        for raw_path in raw_paths:
            node_rows = []
            call_lines = []
            for index, (symbol_id, line) in enumerate(raw_path):
                anchor = anchors_by_id[symbol_id]
                node_rows.append(PathNodeRow(symbol_id=anchor.anchor_id, name=anchor.name, path=anchor.path))
                if index > 0 and line is not None:
                    call_lines.append(line)
            paths.append(
                CallPathRow(
                    hop_count=max(len(node_rows) - 1, 0),
                    nodes=tuple(node_rows),
                    call_lines=tuple(call_lines),
                )
            )
        ordered_paths = tuple(sorted(paths, key=lambda item: (item.hop_count, tuple(node.name for node in item.nodes))))
        status = "truncated" if truncated else ("found" if ordered_paths else "no_path")
        return PathSearchResult(
            status=status,
            returned_path_count=len(ordered_paths),
            truncated=truncated,
            paths=ordered_paths,
        )
```

- [ ] **Step 4: Run the graph-focused query-service tests to verify they pass**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_query_service.py -q
```

Expected:

- PASS with direct caller/callee rows, strict roots, multi-path ordering, and truncation behavior validated

- [ ] **Step 5: Commit the graph query implementation**

```bash
git add src/repo_analysis_tools/query/path_search.py src/repo_analysis_tools/query/service.py tests/fixtures/query_path_repo.py tests/unit/test_query_service.py
git commit -m "feat: add graph queries for minimal query mcp"
```

### Task 4: Replace MCP Registration With The New Nine-Tool Surface

**Files:**
- Modify: `src/repo_analysis_tools/mcp/contracts/scan.py`
- Create: `src/repo_analysis_tools/mcp/contracts/query.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/__init__.py`
- Create: `src/repo_analysis_tools/mcp/scan_registry.py`
- Modify: `src/repo_analysis_tools/mcp/tools/scan_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/query_tools.py`
- Modify: `src/repo_analysis_tools/mcp/tools/__init__.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Modify: `tests/smoke/test_mcp_server.py`
- Create: `tests/integration/test_minimal_query_workflow.py`

- [ ] **Step 1: Rewrite the contract, smoke, and workflow tests for the new surface**

```python
# tests/contract/test_tool_contracts.py
EXPECTED_TOOL_NAMES = {
    "rebuild_repo_snapshot",
    "list_priority_files",
    "get_file_info",
    "list_file_symbols",
    "resolve_symbols",
    "open_symbol_context",
    "query_call_relations",
    "find_root_functions",
    "find_call_paths",
}

LEGACY_TOOL_NAMES = {
    "scan_repo",
    "refresh_scan",
    "get_scan_status",
    "show_scope",
    "list_scope_nodes",
    "explain_scope_node",
    "list_anchors",
    "find_anchor",
    "describe_anchor",
    "plan_slice",
    "inspect_slice",
    "build_evidence_pack",
    "read_evidence_pack",
    "open_span",
    "impact_from_paths",
    "impact_from_anchor",
    "summarize_impact",
    "render_focus_report",
    "render_module_summary",
    "render_analysis_outline",
    "export_analysis_bundle",
    "export_scope_snapshot",
    "export_evidence_bundle",
}

def test_contract_registry_exposes_only_scan_and_query_domains(self) -> None:
    self.assertEqual(set(DOMAIN_CONTRACTS), {"scan", "query"})
    self.assertEqual(set(CONTRACT_BY_NAME), EXPECTED_TOOL_NAMES)
    self.assertTrue(LEGACY_TOOL_NAMES.isdisjoint(CONTRACT_BY_NAME))
```

```python
# tests/smoke/test_mcp_server.py
        self.assertEqual(set(tool_names), EXPECTED_TOOL_NAMES)
        self.assertTrue(LEGACY_TOOL_NAMES.isdisjoint(tool_names))
```

```python
# tests/integration/test_minimal_query_workflow.py
class MinimalQueryWorkflowTest(unittest.TestCase):
    def test_repository_reading_workflow_uses_only_new_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))

            rebuild_payload = rebuild_repo_snapshot(str(repo))
            scan_id = rebuild_payload["data"]["scan_id"]
            priority_payload = list_priority_files(scan_id)
            file_payload = get_file_info(scan_id, "src/main.c")
            symbol_payload = resolve_symbols(scan_id, "flash_init")
            symbol_id = symbol_payload["data"]["matches"][0]["symbol_id"]
            context_payload = open_symbol_context(scan_id, symbol_id, 1)
            relations_payload = query_call_relations(scan_id, symbol_id)
            roots_payload = find_root_functions(scan_id, ["src/main.c", "src/flash.c"])
            paths_payload = find_call_paths(
                scan_id,
                roots_payload["data"]["roots"][0]["symbol_id"],
                symbol_id,
            )

            self.assertEqual(priority_payload["data"]["files"][0]["path"], "src/main.c")
            self.assertTrue(file_payload["data"]["has_main_definition"])
            self.assertEqual(relations_payload["data"]["callers"][0]["name"], "main")
            self.assertIn("flash_init", "\n".join(context_payload["data"]["lines"]))
            self.assertEqual(paths_payload["data"]["status"], "found")
```

- [ ] **Step 2: Run the MCP-facing tests to verify they fail**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/contract/test_tool_contracts.py tests/smoke/test_mcp_server.py tests/integration/test_minimal_query_workflow.py -q
```

Expected:

- FAIL with missing contract names, missing tool registrations, and missing `scan_id` resolution for query wrappers

- [ ] **Step 3: Implement the new contracts, scan registry, and FastMCP wrappers**

```python
# src/repo_analysis_tools/mcp/scan_registry.py
_SCAN_REPO_ROOTS: dict[str, str] = {}

def remember_scan(scan_id: str, repo_root: str) -> None:
    _SCAN_REPO_ROOTS[scan_id] = repo_root

def repo_root_for_scan(scan_id: str) -> str:
    try:
        return _SCAN_REPO_ROOTS[scan_id]
    except KeyError as exc:
        raise FileNotFoundError(f"scan {scan_id} is not known to this MCP session") from exc
```

```python
# src/repo_analysis_tools/mcp/contracts/scan.py
SCAN_CONTRACTS = (
    ToolContract(
        name="rebuild_repo_snapshot",
        domain="scan",
        input_schema={"target_repo": "string"},
        output_schema={
            "scan_id": "scan_<12-hex>",
            "file_count": "int",
            "symbol_count": "int",
            "function_count": "int",
            "call_edge_count": "int",
        },
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.RUNTIME_STATE, ErrorCode.INTERNAL),
        recommended_next_tools=("list_priority_files", "get_file_info"),
    ),
)

# src/repo_analysis_tools/mcp/contracts/query.py
QUERY_CONTRACTS = (
    ToolContract(name="list_priority_files", domain="query", input_schema={"scan_id": "scan_<12-hex>"}, output_schema={"files": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("get_file_info", "list_file_symbols")),
    ToolContract(name="get_file_info", domain="query", input_schema={"scan_id": "scan_<12-hex>", "path": "string"}, output_schema={"path": "string", "role": "string", "priority_score": "int", "line_count": "int", "symbol_count": "int", "function_count": "int", "type_count": "int", "macro_count": "int", "include_count": "int", "incoming_call_count": "int", "outgoing_call_count": "int", "root_function_count": "int", "has_main_definition": "bool"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("list_file_symbols", "find_root_functions")),
    ToolContract(name="list_file_symbols", domain="query", input_schema={"scan_id": "scan_<12-hex>", "paths": "list[string]"}, output_schema={"files": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("open_symbol_context", "resolve_symbols")),
    ToolContract(name="resolve_symbols", domain="query", input_schema={"scan_id": "scan_<12-hex>", "symbol_name": "string"}, output_schema={"match_count": "int", "matches": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("open_symbol_context", "query_call_relations")),
    ToolContract(name="open_symbol_context", domain="query", input_schema={"scan_id": "scan_<12-hex>", "symbol_id": "string", "context_lines": "int"}, output_schema={"symbol_id": "string", "name": "string", "kind": "string", "path": "string", "definition_line_start": "int", "definition_line_end": "int", "context_line_start": "int", "context_line_end": "int", "lines": "list[string]"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("query_call_relations", "find_call_paths")),
    ToolContract(name="query_call_relations", domain="query", input_schema={"scan_id": "scan_<12-hex>", "function_id": "string"}, output_schema={"callers": "list", "callees": "list", "non_resolved_callees": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("find_call_paths", "find_root_functions")),
    ToolContract(name="find_root_functions", domain="query", input_schema={"scan_id": "scan_<12-hex>", "paths": "list[string]"}, output_schema={"roots": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("find_call_paths", "open_symbol_context")),
    ToolContract(name="find_call_paths", domain="query", input_schema={"scan_id": "scan_<12-hex>", "from_function_id": "string", "to_function_id": "string"}, output_schema={"status": "string", "returned_path_count": "int", "truncated": "bool", "paths": "list"}, stable_ids=(), failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL), recommended_next_tools=("open_symbol_context", "query_call_relations")),
)

# src/repo_analysis_tools/mcp/contracts/__init__.py
from repo_analysis_tools.mcp.contracts.query import QUERY_CONTRACTS
from repo_analysis_tools.mcp.contracts.scan import SCAN_CONTRACTS

DOMAIN_CONTRACTS = {
    "scan": SCAN_CONTRACTS,
    "query": QUERY_CONTRACTS,
}

CONTRACT_BY_NAME = {
    contract.name: contract
    for contracts in DOMAIN_CONTRACTS.values()
    for contract in contracts
}
```

```python
# src/repo_analysis_tools/mcp/tools/scan_tools.py
@mcp.tool()
def rebuild_repo_snapshot(target_repo: str) -> dict[str, object]:
    snapshot = ScanService().scan(target_repo)
    anchor_snapshot = AnchorStore.for_repo(target_repo).load(scan_id=snapshot.scan_id)
    remember_scan(snapshot.scan_id, snapshot.repo_root)
    return ok_response(
        data={
            "scan_id": snapshot.scan_id,
            "file_count": snapshot.file_count,
            "symbol_count": len(anchor_snapshot.anchors),
            "function_count": sum(1 for anchor in anchor_snapshot.anchors if anchor.kind == "function_definition"),
            "call_edge_count": sum(1 for relation in anchor_snapshot.relations if relation.kind == "direct_call"),
        },
        messages=[],
        recommended_next_tools=["list_priority_files", "get_file_info"],
    )

# src/repo_analysis_tools/mcp/tools/query_tools.py
def _query_service(scan_id: str) -> tuple[QueryService, str]:
    return QueryService(), repo_root_for_scan(scan_id)

@mcp.tool()
def list_priority_files(scan_id: str) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    rows = service.list_priority_files(repo_root, scan_id)
    return ok_response(data={"files": [{"path": row.path, "priority_score": row.priority_score} for row in rows]}, messages=[], recommended_next_tools=["get_file_info", "list_file_symbols"])

@mcp.tool()
def get_file_info(scan_id: str, path: str) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    row = service.get_file_info(repo_root, scan_id, path)
    return ok_response(data=row.__dict__, messages=[], recommended_next_tools=["list_file_symbols", "find_root_functions"])

@mcp.tool()
def list_file_symbols(scan_id: str, paths: list[str]) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    rows = service.list_file_symbols(repo_root, scan_id, paths)
    return ok_response(data={"files": [{"path": row.path, "symbols": [symbol.__dict__ for symbol in row.symbols]} for row in rows]}, messages=[], recommended_next_tools=["open_symbol_context", "resolve_symbols"])

@mcp.tool()
def resolve_symbols(scan_id: str, symbol_name: str) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    result = service.resolve_symbols(repo_root, scan_id, symbol_name)
    return ok_response(data={"match_count": result.match_count, "matches": [match.__dict__ for match in result.matches]}, messages=[], recommended_next_tools=["open_symbol_context", "query_call_relations"])

@mcp.tool()
def open_symbol_context(scan_id: str, symbol_id: str, context_lines: int) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    row = service.open_symbol_context(repo_root, scan_id, symbol_id, context_lines)
    return ok_response(data={**row.__dict__, "lines": list(row.lines)}, messages=[], recommended_next_tools=["query_call_relations", "find_call_paths"])

@mcp.tool()
def query_call_relations(scan_id: str, function_id: str) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    result = service.query_call_relations(repo_root, scan_id, function_id)
    return ok_response(data={"callers": [row.__dict__ for row in result.callers], "callees": [row.__dict__ for row in result.callees], "non_resolved_callees": [row.__dict__ for row in result.non_resolved_callees]}, messages=[], recommended_next_tools=["find_call_paths", "find_root_functions"])

@mcp.tool()
def find_root_functions(scan_id: str, paths: list[str]) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    roots = service.find_root_functions(repo_root, scan_id, paths)
    return ok_response(data={"roots": [row.__dict__ for row in roots]}, messages=[], recommended_next_tools=["find_call_paths", "open_symbol_context"])

@mcp.tool()
def find_call_paths(scan_id: str, from_function_id: str, to_function_id: str) -> dict[str, object]:
    service, repo_root = _query_service(scan_id)
    result = service.find_call_paths(repo_root, scan_id, from_function_id, to_function_id)
    return ok_response(data={"status": result.status, "returned_path_count": result.returned_path_count, "truncated": result.truncated, "paths": [{"hop_count": path.hop_count, "nodes": [node.__dict__ for node in path.nodes], "call_lines": list(path.call_lines)} for path in result.paths]}, messages=[], recommended_next_tools=["open_symbol_context", "query_call_relations"])

# src/repo_analysis_tools/mcp/tools/__init__.py
from . import query_tools, scan_tools
__all__ = ["query_tools", "scan_tools"]
```

- [ ] **Step 4: Run the MCP-facing tests to verify they pass**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/contract/test_tool_contracts.py tests/smoke/test_mcp_server.py tests/integration/test_minimal_query_workflow.py -q
```

Expected:

- PASS with only the new nine tools registered and callable through the MCP wrappers

- [ ] **Step 5: Commit the MCP surface replacement**

```bash
git add src/repo_analysis_tools/mcp/contracts/scan.py src/repo_analysis_tools/mcp/contracts/query.py src/repo_analysis_tools/mcp/contracts/__init__.py src/repo_analysis_tools/mcp/scan_registry.py src/repo_analysis_tools/mcp/tools/scan_tools.py src/repo_analysis_tools/mcp/tools/query_tools.py src/repo_analysis_tools/mcp/tools/__init__.py tests/contract/test_tool_contracts.py tests/smoke/test_mcp_server.py tests/integration/test_minimal_query_workflow.py
git commit -m "feat: replace mcp surface with minimal query tools"
```

### Task 5: Rewrite Active Docs, Skills, And Demo For The New Surface

**Files:**
- Modify: `README.md`
- Modify: `docs/contracts/mcp-tool-contracts.md`
- Modify: `docs/architecture.md`
- Modify: `docs/self-use-launch.md`
- Modify: `.agents/skills/repo-understand/SKILL.md`
- Modify: `.claude/skills/repo-understand/SKILL.md`
- Modify: `tools/run_self_use_demo.py`
- Modify: `tests/integration/test_self_use_demo.py`
- Modify: `tests/unit/test_architecture_docs.py`
- Modify: `tests/unit/test_client_skill_distribution.py`
- Modify: `tests/unit/test_launch_docs.py`

- [ ] **Step 1: Write the failing documentation, skill, and demo assertions**

```python
# tests/unit/test_architecture_docs.py
    def test_active_architecture_docs_reference_minimal_query_surface(self) -> None:
        architecture = Path("docs/architecture.md").read_text(encoding="utf-8")
        self.assertIn("rebuild_repo_snapshot", architecture)
        self.assertIn("find_call_paths", architecture)
        self.assertNotIn("plan_slice", architecture)
        self.assertNotIn("open_span", architecture)

# tests/unit/test_client_skill_distribution.py
SKILL_NAMES = ["repo-understand"]

# tests/unit/test_launch_docs.py
    def test_readme_contains_codex_first_launch_strings(self) -> None:
        text = self.read_text(README)
        for needle in (
            "rebuild_repo_snapshot",
            "list_priority_files",
            "find_call_paths",
            "/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py",
        ):
            self.assertIn(needle, text)
        for needle in ("plan_slice", "render_module_summary", "export_analysis_bundle"):
            self.assertNotIn(needle, text)

    def test_launch_doc_contains_daily_use_workflow_strings(self) -> None:
        text = self.read_text(LAUNCH_DOC)
        for needle in (
            "rebuild_repo_snapshot",
            "list_priority_files",
            "open_symbol_context",
            "query_call_relations",
            "find_call_paths",
        ):
            self.assertIn(needle, text)
        for needle in ("refresh_scan", "build_evidence_pack", "render_module_summary"):
            self.assertNotIn(needle, text)
```

```python
# tests/integration/test_self_use_demo.py
class SelfUseDemoIntegrationTest(unittest.TestCase):
    def test_self_use_demo_emits_expected_json_summary(self) -> None:
        result = subprocess.run(
            ["/home/hyx/anaconda3/envs/agent/bin/python", str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        payload = json.loads(result.stdout)
        self.assertRegex(payload["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertEqual(payload["symbol_name"], "easyflash_init")
        self.assertGreaterEqual(len(payload["priority_files"]), 1)
        self.assertGreaterEqual(payload["caller_count"], 0)
        self.assertIn(payload["call_path_status"], {"found", "no_path", "truncated"})
```

```markdown
# .agents/skills/repo-understand/SKILL.md
## Required Tool Order

rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

- [ ] **Step 2: Run the doc, skill, and demo tests to verify they fail**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_architecture_docs.py tests/unit/test_launch_docs.py tests/unit/test_client_skill_distribution.py tests/integration/test_self_use_demo.py -q
```

Expected:

- FAIL because active docs, mirrored skills, and the demo script still describe or invoke the removed legacy tools

- [ ] **Step 3: Rewrite the active docs, mirrored skill, and demo**

```markdown
# README.md
## Current MCP Surface

- `rebuild_repo_snapshot`
- `list_priority_files`
- `get_file_info`
- `list_file_symbols`
- `resolve_symbols`
- `open_symbol_context`
- `query_call_relations`
- `find_root_functions`
- `find_call_paths`

## Codex Quickstart

Run `/home/hyx/anaconda3/envs/agent/bin/python tools/run_self_use_demo.py` to exercise the query-first workflow end to end.
```

```markdown
# docs/contracts/mcp-tool-contracts.md
## Query-First Mainline

rebuild_repo_snapshot
-> list_priority_files
-> get_file_info
-> list_file_symbols / resolve_symbols
-> open_symbol_context / query_call_relations / find_root_functions / find_call_paths
```

```markdown
# docs/self-use-launch.md
## Daily Workflow

1. `rebuild_repo_snapshot`
2. `list_priority_files`
3. `get_file_info`
4. `list_file_symbols` or `resolve_symbols`
5. `open_symbol_context`, `query_call_relations`, `find_root_functions`, or `find_call_paths`
```

```python
# tools/run_self_use_demo.py
from repo_analysis_tools.mcp.tools.query_tools import (
    find_call_paths,
    find_root_functions,
    list_priority_files,
    open_symbol_context,
    query_call_relations,
    resolve_symbols,
)
from repo_analysis_tools.mcp.tools.scan_tools import rebuild_repo_snapshot

def run_demo() -> dict[str, object]:
    repo = materialize_easyflash_repo(Path(tempfile.mkdtemp(prefix="self-use-demo-")))
    rebuild_payload = rebuild_repo_snapshot(str(repo))
    scan_id = rebuild_payload["data"]["scan_id"]
    priority_payload = list_priority_files(scan_id)
    symbol_payload = resolve_symbols(scan_id, "easyflash_init")
    symbol_row = symbol_payload["data"]["matches"][0]
    context_payload = open_symbol_context(scan_id, symbol_row["symbol_id"], 2)
    relations_payload = query_call_relations(scan_id, symbol_row["symbol_id"])
    roots_payload = find_root_functions(scan_id, ["easyflash/src/easyflash.c", "easyflash/port/ef_port.c"])
    call_path_status = "no_path"
    call_path_count = 0
    if roots_payload["data"]["roots"]:
        path_payload = find_call_paths(
            scan_id,
            roots_payload["data"]["roots"][0]["symbol_id"],
            symbol_row["symbol_id"],
        )
        call_path_status = path_payload["data"]["status"]
        call_path_count = path_payload["data"]["returned_path_count"]
    return {
        "repo_root": str(repo),
        "scan_id": scan_id,
        "priority_files": priority_payload["data"]["files"][:5],
        "symbol_name": symbol_row["name"],
        "symbol_path": symbol_row["path"],
        "context_line_start": context_payload["data"]["context_line_start"],
        "context_line_end": context_payload["data"]["context_line_end"],
        "caller_count": len(relations_payload["data"]["callers"]),
        "callee_count": len(relations_payload["data"]["callees"]),
        "root_names": [row["name"] for row in roots_payload["data"]["roots"]],
        "call_path_status": call_path_status,
        "call_path_count": call_path_count,
    }
```

- [ ] **Step 4: Run the documentation, skill, and demo tests to verify they pass**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/unit/test_architecture_docs.py tests/unit/test_launch_docs.py tests/unit/test_client_skill_distribution.py tests/integration/test_self_use_demo.py -q
```

Expected:

- PASS with active docs, mirrored skills, and the demo script aligned to the query-only workflow

- [ ] **Step 5: Commit the active-doc, skill, and demo rewrite**

```bash
git add README.md docs/contracts/mcp-tool-contracts.md docs/architecture.md docs/self-use-launch.md .agents/skills/repo-understand/SKILL.md .claude/skills/repo-understand/SKILL.md tools/run_self_use_demo.py tests/integration/test_self_use_demo.py tests/unit/test_architecture_docs.py tests/unit/test_client_skill_distribution.py tests/unit/test_launch_docs.py
git commit -m "docs: rewrite active workflows for minimal query mcp"
```

### Task 6: Purge Legacy Interface Files From The Active Tree

**Files:**
- Modify: `tests/smoke/test_package_layout.py`
- Remove manually: everything listed in `Required Manual Purge Commands (User-Run Only)`

- [ ] **Step 1: Write the failing absence assertions for the legacy surface**

```python
# tests/smoke/test_package_layout.py
UNEXPECTED_FILES = [
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "anchors.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "evidence.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "export.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "impact.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "report.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "scope.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "contracts" / "slice.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "anchors_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "evidence_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "export_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "impact_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "report_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "scope_tools.py",
    ROOT / "src" / "repo_analysis_tools" / "mcp" / "tools" / "slice_tools.py",
    ROOT / ".agents" / "skills" / "analysis-writing" / "SKILL.md",
    ROOT / ".agents" / "skills" / "analysis-maintenance" / "SKILL.md",
    ROOT / ".agents" / "skills" / "change-impact" / "SKILL.md",
    ROOT / ".claude" / "skills" / "analysis-writing" / "SKILL.md",
    ROOT / ".claude" / "skills" / "analysis-maintenance" / "SKILL.md",
    ROOT / ".claude" / "skills" / "change-impact" / "SKILL.md",
    ROOT / "tests" / "integration" / "test_analysis_writing_workflow.py",
    ROOT / "tests" / "integration" / "test_change_impact_workflow.py",
    ROOT / "tests" / "integration" / "test_export_reuse_workflow.py",
    ROOT / "tests" / "integration" / "test_mainline_mcp_workflow.py",
    ROOT / "tests" / "e2e" / "test_analysis_writing_easyflash.py",
    ROOT / "tests" / "e2e" / "test_change_impact_easyflash.py",
    ROOT / "tests" / "e2e" / "test_export_easyflash.py",
    ROOT / "tests" / "e2e" / "test_repo_understand_easyflash.py",
    ROOT / "tests" / "e2e" / "test_self_use_launch_easyflash.py",
    ROOT / "tests" / "golden" / "test_contract_golden.py",
    ROOT / "tests" / "golden" / "fixtures" / "export_analysis_bundle_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "export_evidence_bundle_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "export_scope_snapshot_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "read_evidence_pack_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "render_module_summary_scope_first.json",
    ROOT / "tests" / "golden" / "fixtures" / "scan_repo.json",
    ROOT / "tests" / "golden" / "fixtures" / "summarize_impact_scope_first.json",
]

    def test_legacy_interface_files_are_removed_from_active_tree(self) -> None:
        for path in UNEXPECTED_FILES:
            self.assertFalse(path.exists(), str(path))
```

- [ ] **Step 2: Run the package-layout test to verify it fails before the purge**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/smoke/test_package_layout.py -q
```

Expected:

- FAIL while the old contract files, wrapper files, skills, and workflow tests still exist on disk

- [ ] **Step 3: Execute the manual purge commands**

Run exactly the commands listed under `Required Manual Purge Commands (User-Run Only)` in this plan.

- [ ] **Step 4: Re-run the package-layout test to verify the purge**

Run:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest tests/smoke/test_package_layout.py -q
```

Expected:

- PASS with the legacy MCP surface fully absent from the active tree

- [ ] **Step 5: Commit the purge**

```bash
git add tests/smoke/test_package_layout.py src/repo_analysis_tools/mcp/contracts src/repo_analysis_tools/mcp/tools .agents/skills .claude/skills tests/integration tests/e2e tests/golden
git commit -m "chore: purge legacy mcp surface"
```

## Final Verification

After all six tasks are complete and the manual purge step has been handled by a human, run the new active suite:

```bash
PYTHONPATH=src /home/hyx/anaconda3/envs/agent/bin/python -m pytest \
  tests/unit/test_scope_service.py \
  tests/unit/test_scan_service.py \
  tests/unit/test_query_service.py \
  tests/contract/test_tool_contracts.py \
  tests/integration/test_minimal_query_workflow.py \
  tests/integration/test_self_use_demo.py \
  tests/smoke/test_mcp_server.py \
  tests/smoke/test_package_layout.py \
  tests/unit/test_architecture_docs.py \
  tests/unit/test_client_skill_distribution.py \
  tests/unit/test_launch_docs.py -q
```

Expected:

- all selected tests pass
- MCP server smoke test lists only the nine new tools
- the self-use demo uses only the new query-first workflow
- the active tree no longer contains the removed legacy interface files

## Spec Self-Review

Coverage check:

- `rebuild_repo_snapshot`: Task 4
- `list_priority_files` / `get_file_info`: Tasks 1, 2, and 4
- `list_file_symbols` / `resolve_symbols` / `open_symbol_context`: Tasks 2 and 4
- `query_call_relations` / `find_root_functions` / `find_call_paths`: Tasks 3 and 4
- persisted scope file facts: Task 1
- active doc/skill/demo rewrite: Task 5
- no compatibility surface and no retained legacy files: Task 4 registration replacement plus Task 6 manual purge

Placeholder scan:

- no `TODO`
- no `TBD`
- no placeholder ellipses used to skip implementation detail

Consistency check:

- `scan_id` is the only query handle after rebuild
- `symbol_id` is backed by existing `anchor_id`
- scope remains file-level only throughout the plan
- MCP query wrappers resolve repo roots only through the new `scan_id` registry

Plan complete and saved to `docs/superpowers/plans/2026-04-20-m7-minimal-query-mcp.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
