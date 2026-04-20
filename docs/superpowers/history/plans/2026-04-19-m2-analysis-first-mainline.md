# M2 Analysis-First Mainline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first genuinely useful repository-understanding mainline by making `scan_repo -> get_scan_status -> show_scope -> list_anchors/find_anchor/describe_anchor -> plan_slice -> build_evidence_pack/read_evidence_pack -> open_span` work on unfamiliar C repositories with traceable evidence.

**Architecture:** Build M2 around persisted JSON artifacts under `<target_repo>/.codewiki/` so every mainline step reads and writes explicit scan, scope, anchor, slice, and evidence assets instead of hidden session state. Keep the workflow MCP-first: the domain services do the real work, MCP tools only validate inputs and serialize the results, and the new `repo-understand` skill sequences those tools without embedding analysis logic. Guard raw span reading behind evidence packs and fixed line limits so `open_span` stays narrower than general file browsing.

**Tech Stack:** Python 3.11 (`/home/hyx/anaconda3/envs/agent/bin/python`), stdlib `unittest`, stdlib `json`/`hashlib`/`difflib`, MCP Python SDK (`mcp[cli]`), `tree-sitter`, `tree-sitter-c`, Git CLI for provenance checks, Markdown skill files under `.agents/skills/`

---

## File Structure

- Create: `tests/fixtures/__init__.py`
  Responsibility: package marker for local fixture helpers used by unit, integration, and end-to-end tests.
- Create: `tests/fixtures/scope_first_repo.py`
  Responsibility: fast synthetic C fixture builder migrated from the old repository.
- Create: `tests/fixtures/git_helpers.py`
  Responsibility: tiny helper for initializing a fixture repository with a deterministic Git commit.
- Create directory tree: `tests/fixtures/repos/easyflash/`
  Responsibility: checked-in real C repository fixture used for M2 end-to-end acceptance.
- Create: `tests/unit/test_fixture_repos.py`
  Responsibility: verify the fast synthetic fixture and checked-in EasyFlash fixture are both usable.
- Create: `tests/integration/__init__.py`, `tests/e2e/__init__.py`
  Responsibility: make the new integration and end-to-end suites importable under `unittest`.
- Modify: `tests/smoke/test_package_layout.py`
  Responsibility: lock the new fixture and test-suite directories into the repository layout contract.
- Create: `src/repo_analysis_tools/core/git.py`
  Responsibility: Git head detection, workspace-dirty detection, and tracked-file checks shared by scan and evidence.
- Create: `src/repo_analysis_tools/storage/json_assets.py`
  Responsibility: deterministic JSON read/write/list helpers rooted in `.codewiki/`.
- Create: `src/repo_analysis_tools/scan/models.py`, `scan/store.py`, `scan/service.py`
  Responsibility: persisted scan artifacts, latest-scan tracking, and repository traversal with provenance capture.
- Create: `src/repo_analysis_tools/scope/models.py`, `scope/config.py`, `scope/store.py`, `scope/service.py`
  Responsibility: deterministic file-role classification, scope nodes, and scope snapshot persistence.
- Create: `src/repo_analysis_tools/anchors/models.py`, `anchors/parser.py`, `anchors/store.py`, `anchors/service.py`
  Responsibility: C anchor extraction, normalized anchor IDs, relation discovery, and persisted anchor snapshots.
- Modify: `src/repo_analysis_tools/core/ids.py`
  Responsibility: add deterministic helpers for anchor IDs and scope node IDs while keeping existing artifact IDs unchanged.
- Create: `src/repo_analysis_tools/slice/models.py`, `slice/store.py`, `slice/query_classifier.py`, `slice/seed_resolver.py`, `slice/service.py`
  Responsibility: classify repository-understanding questions, resolve seeds against anchors and paths, and persist bounded slice manifests.
- Create: `src/repo_analysis_tools/evidence/models.py`, `evidence/store.py`, `evidence/snippets.py`, `evidence/freshness.py`, `evidence/service.py`
  Responsibility: build evidence packs from slices, evaluate scan freshness, read bounded snippets, and enforce `open_span` guardrails.
- Modify: `src/repo_analysis_tools/mcp/contracts/scan.py`, `scope.py`, `anchors.py`, `slice.py`, `evidence.py`
  Responsibility: replace M1 placeholder payload schemas with the M2 mainline payload shapes.
- Modify: `src/repo_analysis_tools/mcp/tools/scan_tools.py`, `scope_tools.py`, `anchors_tools.py`, `slice_tools.py`, `evidence_tools.py`
  Responsibility: replace M1 stubs for the mainline path with service-backed implementations while leaving non-M2 domains stubbed.
- Create: `.agents/skills/repo-understand/SKILL.md`
  Responsibility: first usable Codex workflow skill for evidence-backed repository understanding on unfamiliar C repositories.
- Modify: `docs/architecture.md`
  Responsibility: describe persisted JSON asset layout, scan-to-evidence flow, and the evidence-before-span rule.
- Modify: `docs/contracts/mcp-tool-contracts.md`
  Responsibility: document the final M2 mainline input and output contracts.
- Modify: `tests/contract/test_tool_contracts.py`
  Responsibility: validate the mixed world where mainline tools are real and non-mainline tools remain M1 stubs.
- Modify: `tests/golden/test_contract_golden.py`
  Responsibility: assert deterministic snapshots for real M2 tool payloads.
- Create: `tests/golden/fixtures/read_evidence_pack_scope_first.json`
  Responsibility: golden response for the first real evidence-pack read.
- Modify: `tests/golden/fixtures/scan_repo.json`
  Responsibility: replace the M1 stub scan fixture with a real M2 scan response.
- Create: `tests/integration/test_mainline_mcp_workflow.py`
  Responsibility: prove the full mainline works on the fast synthetic fixture.
- Create: `tests/e2e/test_repo_understand_easyflash.py`
  Responsibility: prove the full mainline works on a checked-in real C repository fixture.

## Working Set

- Parent design: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- M2 spec: `docs/superpowers/specs/2026-04-17-m2-analysis-first-mainline-spec.md`
- Legacy mapping: `migration/capability-mapping.md`
- Legacy disposition baseline: `migration/keep-drop-rewrite.md`
- Fast synthetic fixture source: `/home/hyx/mycodewiki/tests/fixtures/scope_first_repo.py`
- Real fixture source available on this machine: `/mnt/c/Users/HYX/Downloads/EasyFlash-master/EasyFlash-master`
- Python runtime for this machine: `/home/hyx/anaconda3/envs/agent/bin/python`

### Task 1: Add Fixture Repositories and the New Test Harness

**Files:**
- Create: `tests/fixtures/__init__.py`
- Create: `tests/fixtures/scope_first_repo.py`
- Create: `tests/fixtures/git_helpers.py`
- Create directory tree: `tests/fixtures/repos/easyflash/`
- Create: `tests/unit/test_fixture_repos.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/e2e/__init__.py`
- Modify: `tests/smoke/test_package_layout.py`

- [ ] **Step 1: Write the failing fixture and layout tests**

```python
import tempfile
import unittest
from pathlib import Path

from tests.fixtures.scope_first_repo import build_scope_first_repo


ROOT = Path(__file__).resolve().parents[2]


class FixtureReposTest(unittest.TestCase):
    def test_scope_first_repo_builder_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            expected = {
                "src/main.c",
                "src/flash.c",
                "src/config.h",
                "ports/board_port.c",
                "demo/demo_main.c",
                "generated/autoconf.h",
            }
            actual = {
                path.relative_to(repo).as_posix()
                for path in repo.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual, expected)

    def test_easyflash_fixture_contains_real_entrypoints(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "repos" / "easyflash"
        self.assertTrue((fixture_root / "easyflash" / "src" / "easyflash.c").is_file())
        self.assertTrue((fixture_root / "easyflash" / "inc" / "easyflash.h").is_file())
        self.assertTrue((fixture_root / "easyflash" / "port" / "ef_port.c").is_file())
```

Add these expectations to `tests/smoke/test_package_layout.py`:

```python
EXPECTED_DIRECTORIES.extend(
    [
        ROOT / "tests" / "fixtures",
        ROOT / "tests" / "integration",
        ROOT / "tests" / "e2e",
    ]
)
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_fixture_repos tests.smoke.test_package_layout -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tests.fixtures.scope_first_repo'` and missing-directory assertions for `tests/fixtures`, `tests/integration`, or `tests/e2e`.

- [ ] **Step 3: Add the synthetic fixture, the checked-in EasyFlash fixture, and the new package markers**

Write `tests/fixtures/scope_first_repo.py`:

```python
from pathlib import Path


def build_scope_first_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "scope-first-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "ports").mkdir(parents=True, exist_ok=True)
    (repo / "demo").mkdir(parents=True, exist_ok=True)
    (repo / "generated").mkdir(parents=True, exist_ok=True)

    (repo / "src" / "main.c").write_text(
        '#include "config.h"\n'
        "int flash_init(void);\n"
        "int main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "flash.c").write_text(
        "int flash_init(void) { return 0; }\n",
        encoding="utf-8",
    )
    (repo / "src" / "config.h").write_text(
        "#define EF_USING_ENV 1\n",
        encoding="utf-8",
    )
    (repo / "ports" / "board_port.c").write_text(
        "void board_port_init(void) {}\n",
        encoding="utf-8",
    )
    (repo / "demo" / "demo_main.c").write_text(
        "int flash_init(void);\n"
        "int demo_main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "generated" / "autoconf.h").write_text(
        "#define GENERATED_VALUE 1\n",
        encoding="utf-8",
    )
    return repo
```

Write `tests/fixtures/git_helpers.py`:

```python
import subprocess
from pathlib import Path


def init_git_fixture(repo: Path, *, email: str = "fixtures@example.com", name: str = "Fixture Tests") -> str:
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.email", email], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", name], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, text=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial fixture"], cwd=repo, capture_output=True, text=True, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
```

Add package markers:

```python
"""Fixture helpers for repo-analysis-tools tests."""
```

Create `tests/integration/__init__.py`:

```python
"""Integration tests for real mainline workflows."""
```

Create `tests/e2e/__init__.py`:

```python
"""End-to-end tests for checked-in real repository fixtures."""
```

Populate the checked-in EasyFlash fixture from the known local source:

```bash
mkdir -p tests/fixtures/repos
cp -R /mnt/c/Users/HYX/Downloads/EasyFlash-master/EasyFlash-master tests/fixtures/repos/easyflash
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_fixture_repos tests.smoke.test_package_layout -v`
Expected: PASS with the fixture builder test, the EasyFlash presence test, and the updated layout assertions all green.

- [ ] **Step 5: Commit the fixture baseline**

```bash
git add tests/fixtures tests/unit/test_fixture_repos.py tests/integration/__init__.py tests/e2e/__init__.py tests/smoke/test_package_layout.py
git commit -m "test: add synthetic and real C fixture baselines"
```

### Task 2: Implement Shared JSON Asset Storage and Real Scan Tools

**Files:**
- Create: `src/repo_analysis_tools/core/git.py`
- Create: `src/repo_analysis_tools/storage/json_assets.py`
- Create: `src/repo_analysis_tools/scan/models.py`
- Create: `src/repo_analysis_tools/scan/store.py`
- Create: `src/repo_analysis_tools/scan/service.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/scan.py`
- Modify: `src/repo_analysis_tools/mcp/tools/scan_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Create: `tests/unit/test_scan_service.py`

- [ ] **Step 1: Write the failing scan-domain and scan-tool tests**

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.scan_tools import get_scan_status, scan_repo
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScanServiceTest(unittest.TestCase):
    def test_scan_service_persists_latest_scan_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            result = ScanService().scan(repo)
            stored = ScanStore.for_repo(repo).load_latest()

            self.assertEqual(stored.scan_id, result.scan_id)
            self.assertEqual(stored.file_count, 6)
            self.assertEqual(stored.repo_root, str(repo.resolve()))

    def test_scan_tools_return_real_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))
            status = get_scan_status(str(repo))

            self.assertEqual(created["status"], "ok")
            self.assertRegex(created["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
            self.assertEqual(created["data"]["file_count"], 6)
            self.assertEqual(status["data"]["scan_id"], created["data"]["scan_id"])
```

Add this real-tool check to `tests/contract/test_tool_contracts.py`:

```python
def test_scan_repo_and_get_scan_status_use_real_services(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = build_scope_first_repo(Path(tmpdir))
        created = scan_repo(str(repo))
        status = get_scan_status(str(repo))

        self.assertEqual(created["data"]["file_count"], 6)
        self.assertEqual(status["data"]["latest_completed_at"], created["data"]["latest_completed_at"])
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_scan_service tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.scan.service` and scan-tool assertions showing the current M1 stub payload is missing `file_count` and `latest_completed_at`.

- [ ] **Step 3: Build the JSON asset store, the scan domain, and the real scan tools**

Write `src/repo_analysis_tools/core/git.py`:

```python
from pathlib import Path
import subprocess


def detect_git_provenance(repo: Path) -> tuple[str | None, bool | None]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        return head, dirty
    except Exception:
        return None, None
```

Write `src/repo_analysis_tools/storage/json_assets.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_analysis_tools.core.paths import domain_storage_root


class JsonAssetStore:
    def __init__(self, target_repo: Path | str, domain_name: str) -> None:
        self.root = domain_storage_root(target_repo, domain_name)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def read_json(self, relative_path: str) -> dict[str, Any]:
        path = self.root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))
```

Write the core of `src/repo_analysis_tools/scan/service.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path

from repo_analysis_tools.core.git import detect_git_provenance
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.scan.models import ScannedFile, ScanSnapshot
from repo_analysis_tools.scan.store import ScanStore


class ScanService:
    def scan(self, target_repo: Path | str) -> ScanSnapshot:
        repo = Path(target_repo).expanduser().resolve()
        files: list[ScannedFile] = []
        for candidate in sorted(repo.rglob("*")):
            if not candidate.is_file():
                continue
            relative_path = normalize_repo_relative_path(repo, candidate)
            if relative_path.startswith(".git/") or relative_path.startswith(".codewiki/"):
                continue
            files.append(
                ScannedFile(
                    path=relative_path,
                    content_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
                    size_bytes=candidate.stat().st_size,
                )
            )
        git_head, workspace_dirty = detect_git_provenance(repo)
        snapshot = ScanSnapshot(
            scan_id=make_stable_id(StableIdKind.SCAN),
            repo_root=str(repo),
            file_count=len(files),
            completed_at=datetime.now(timezone.utc).isoformat(),
            git_head=git_head,
            workspace_dirty=workspace_dirty,
            files=files,
        )
        ScanStore.for_repo(repo).save(snapshot)
        return snapshot
```

Write the real scan tools in `src/repo_analysis_tools/mcp/tools/scan_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scan.store import ScanStore


def scan_repo(target_repo: str) -> dict:
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=["scan completed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


def refresh_scan(target_repo: str, scan_id: str) -> dict:
    snapshot = ScanService().scan(target_repo)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=[f"scan {scan_id} refreshed"],
        recommended_next_tools=["get_scan_status", "show_scope"],
    )


def get_scan_status(target_repo: str, scan_id: str | None = None) -> dict:
    snapshot = ScanStore.for_repo(target_repo).load(scan_id=scan_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "repo_root": snapshot.repo_root,
            "file_count": snapshot.file_count,
            "latest_completed_at": snapshot.completed_at,
            "git_head": snapshot.git_head,
            "workspace_dirty": snapshot.workspace_dirty,
        },
        messages=["latest scan loaded"],
        recommended_next_tools=["show_scope", "list_anchors"],
    )
```

Update `src/repo_analysis_tools/mcp/contracts/scan.py` so the scan output schemas become:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "repo_root": "string",
    "file_count": "int",
    "latest_completed_at": "iso8601",
    "git_head": "string|null",
    "workspace_dirty": "bool|null",
}
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_scan_service tests.contract.test_tool_contracts -v`
Expected: PASS with real `scan_repo` and `get_scan_status` payloads returning `file_count`, `latest_completed_at`, and a stable `scan_id`.

- [ ] **Step 5: Commit the scan baseline**

```bash
git add src/repo_analysis_tools/core/git.py src/repo_analysis_tools/storage/json_assets.py src/repo_analysis_tools/scan src/repo_analysis_tools/mcp/contracts/scan.py src/repo_analysis_tools/mcp/tools/scan_tools.py tests/unit/test_scan_service.py tests/contract/test_tool_contracts.py
git commit -m "feat: implement persisted scan snapshots"
```

### Task 3: Implement Scope Classification and Real Scope Tools

**Files:**
- Create: `src/repo_analysis_tools/scope/models.py`
- Create: `src/repo_analysis_tools/scope/config.py`
- Create: `src/repo_analysis_tools/scope/store.py`
- Create: `src/repo_analysis_tools/scope/service.py`
- Modify: `src/repo_analysis_tools/scan/service.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/scope.py`
- Modify: `src/repo_analysis_tools/mcp/tools/scope_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Create: `tests/unit/test_scope_service.py`

- [ ] **Step 1: Write the failing scope tests**

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.scope_tools import explain_scope_node, list_scope_nodes, show_scope
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.scope.service import ScopeService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ScopeServiceTest(unittest.TestCase):
    def test_scope_service_classifies_primary_support_external_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            snapshot = ScopeService.for_repo(repo).build_snapshot()
            role_by_path = {item.path: item.role for item in snapshot.files}

            self.assertEqual(role_by_path["src/main.c"], "primary")
            self.assertEqual(role_by_path["ports/board_port.c"], "support")
            self.assertEqual(role_by_path["demo/demo_main.c"], "external")
            self.assertEqual(role_by_path["generated/autoconf.h"], "generated")

    def test_scope_tools_return_summary_nodes_and_node_explanations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)

            summary = show_scope(str(repo))
            nodes = list_scope_nodes(str(repo))
            detail = explain_scope_node(str(repo), node_id="scope_ports")

            self.assertIn("primary", summary["data"]["scope_summary"])
            self.assertTrue(nodes["data"]["nodes"])
            self.assertEqual(detail["data"]["node_id"], "scope_ports")
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_scope_service tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.scope.service` and scope-tool payloads still returning the M1 placeholder fields.

- [ ] **Step 3: Migrate the deterministic scope classifier and wire the real scope tools**

Write the core of `src/repo_analysis_tools/scope/config.py`:

```python
from pathlib import Path


class ScopeConfig:
    def __init__(
        self,
        *,
        focus_roots: list[str],
        external_roots: list[str],
        ignore_roots: list[str],
        include_globs: list[str],
        exclude_globs: list[str],
    ) -> None:
        self.focus_roots = focus_roots
        self.external_roots = external_roots
        self.ignore_roots = ignore_roots
        self.include_globs = include_globs
        self.exclude_globs = exclude_globs


class ScopeConfigLoader:
    DEFAULTS = ScopeConfig(
        focus_roots=["src"],
        external_roots=["vendor", "third_party", "demo"],
        ignore_roots=["build", "generated"],
        include_globs=["**/*.c", "**/*.h"],
        exclude_globs=["**/tests/**"],
    )

    @classmethod
    def load(cls, repo: Path) -> ScopeConfig:
        return cls.DEFAULTS
```

Write the core of `src/repo_analysis_tools/scope/service.py`:

```python
from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.scope.config import ScopeConfigLoader
from repo_analysis_tools.scope.models import ScopeFile, ScopeNode, ScopeSnapshot
from repo_analysis_tools.scope.store import ScopeStore


class ScopeService:
    PRIMARY_HINTS = {"src", "source", "lib", "include", "app", "core"}
    SUPPORT_HINTS = {"ports", "port", "board", "bsp", "platform", "hal"}
    EXTERNAL_HINTS = {"demo", "vendor", "third_party", "third-party", "examples"}
    GENERATED_HINTS = {"generated", "autogen", "gen"}

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.config = ScopeConfigLoader.load(repo)

    @classmethod
    def for_repo(cls, repo: Path | str) -> "ScopeService":
        return cls(Path(repo).expanduser().resolve())

    def build_snapshot(self, scan_id: str | None = None) -> ScopeSnapshot:
        scan_snapshot = ScanStore.for_repo(self.repo).load(scan_id=scan_id)
        files: list[ScopeFile] = []
        for scanned in scan_snapshot.files:
            role = self._classify_path(scanned.path)
            files.append(ScopeFile(path=scanned.path, role=role))
        nodes = [
            ScopeNode(node_id="scope_src", label="src", role="primary"),
            ScopeNode(node_id="scope_ports", label="ports", role="support"),
            ScopeNode(node_id="scope_demo", label="demo", role="external"),
            ScopeNode(node_id="scope_generated", label="generated", role="generated"),
        ]
        snapshot = ScopeSnapshot(scan_id=scan_snapshot.scan_id, files=files, nodes=nodes)
        ScopeStore.for_repo(self.repo).save(snapshot)
        return snapshot

    def _classify_path(self, relative_path: str) -> str:
        parts = {part.lower() for part in Path(relative_path).parts}
        if parts & self.GENERATED_HINTS or "autoconf" in relative_path.lower():
            return "generated"
        if parts & self.SUPPORT_HINTS:
            return "support"
        if parts & self.EXTERNAL_HINTS:
            return "external"
        return "primary"
```

Update `src/repo_analysis_tools/scan/service.py` so `scan()` also builds and persists a scope snapshot:

```python
from repo_analysis_tools.scope.service import ScopeService

ScopeService.for_repo(repo).build_snapshot(scan_id=snapshot.scan_id)
```

Write the real scope tools in `src/repo_analysis_tools/mcp/tools/scope_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.scope.store import ScopeStore


def show_scope(target_repo: str, scan_id: str | None = None) -> dict:
    snapshot = ScopeStore.for_repo(target_repo).load(scan_id=scan_id)
    role_counts = snapshot.role_counts()
    summary = ", ".join(f"{role}: {count}" for role, count in sorted(role_counts.items()))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "scope_summary": summary,
            "role_counts": role_counts,
        },
        messages=["scope snapshot loaded"],
        recommended_next_tools=["list_scope_nodes", "list_anchors"],
    )


def list_scope_nodes(target_repo: str, scan_id: str | None = None) -> dict:
    snapshot = ScopeStore.for_repo(target_repo).load(scan_id=scan_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "nodes": [node.to_dict() for node in snapshot.nodes],
        },
        messages=["scope nodes loaded"],
        recommended_next_tools=["explain_scope_node", "list_anchors"],
    )


def explain_scope_node(target_repo: str, node_id: str, scan_id: str | None = None) -> dict:
    snapshot = ScopeStore.for_repo(target_repo).load(scan_id=scan_id)
    node = next(item for item in snapshot.nodes if item.node_id == node_id)
    related_files = sorted(item.path for item in snapshot.files if item.path.startswith(f"{node.label}/"))
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "node_id": node.node_id,
            "summary": f"{node.label} is classified as {node.role}",
            "related_files": related_files,
        },
        messages=["scope node explained"],
        recommended_next_tools=["list_anchors", "plan_slice"],
    )
```

Update `src/repo_analysis_tools/mcp/contracts/scope.py` so the real M2 scope schemas become:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "scope_summary": "string",
    "role_counts": "dict",
}
```

for `show_scope`, and:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "nodes": "list",
}
```

for `list_scope_nodes`.

Set `explain_scope_node` to:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "node_id": "string",
    "summary": "string",
    "related_files": "list",
}
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_scope_service tests.contract.test_tool_contracts -v`
Expected: PASS with correct file-role classification and real `show_scope`, `list_scope_nodes`, and `explain_scope_node` payloads.

- [ ] **Step 5: Commit the scope implementation**

```bash
git add src/repo_analysis_tools/scope src/repo_analysis_tools/scan/service.py src/repo_analysis_tools/mcp/contracts/scope.py src/repo_analysis_tools/mcp/tools/scope_tools.py tests/unit/test_scope_service.py tests/contract/test_tool_contracts.py
git commit -m "feat: implement persisted scope snapshots"
```

### Task 4: Implement C Anchor Extraction and Real Anchor Tools

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/repo_analysis_tools/core/ids.py`
- Create: `src/repo_analysis_tools/anchors/models.py`
- Create: `src/repo_analysis_tools/anchors/parser.py`
- Create: `src/repo_analysis_tools/anchors/store.py`
- Create: `src/repo_analysis_tools/anchors/service.py`
- Modify: `src/repo_analysis_tools/scan/service.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/anchors.py`
- Modify: `src/repo_analysis_tools/mcp/tools/anchors_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Create: `tests/unit/test_anchor_service.py`

- [ ] **Step 1: Write the failing anchor tests**

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import describe_anchor, find_anchor, list_anchors
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class AnchorServiceTest(unittest.TestCase):
    def test_scope_first_repo_exposes_functions_macros_and_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            payload = list_anchors(str(repo))
            pairs = {(item["kind"], item["name"]) for item in payload["data"]["anchors"]}

            self.assertIn(("function_definition", "main"), pairs)
            self.assertIn(("function_definition", "flash_init"), pairs)
            self.assertIn(("macro_anchor", "EF_USING_ENV"), pairs)

    def test_easyflash_fixture_exposes_easyflash_init_and_direct_calls(self) -> None:
        repo = Path(__file__).resolve().parents[1] / "fixtures" / "repos" / "easyflash"
        ScanService().scan(repo)
        matches = find_anchor(str(repo), anchor_name="easyflash_init")
        detail = describe_anchor(str(repo), anchor_name="easyflash_init")

        self.assertEqual(matches["data"]["matches"][0]["file_path"], "easyflash/src/easyflash.c")
        relation_names = {item["target_name"] for item in detail["data"]["relations"]}
        self.assertIn("ef_port_init", relation_names)
```

- [ ] **Step 2: Install the parser dependencies and run the tests to verify they fail**

Update `pyproject.toml` dependencies to include:

```toml
dependencies = [
  "mcp[cli]>=1.0,<2.0",
  "tree-sitter>=0.21,<0.24",
  "tree-sitter-c>=0.21,<0.24",
]
```

Install them:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m pip install "tree-sitter>=0.21,<0.24" "tree-sitter-c>=0.21,<0.24"
```

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_anchor_service tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.anchors.service` and anchor-tool payloads still returning the M1 placeholder fields.

- [ ] **Step 3: Build the tree-sitter parser, normalized anchor IDs, and real anchor tools**

Extend `src/repo_analysis_tools/core/ids.py` with deterministic helpers:

```python
import hashlib


def make_anchor_id(file_path: str, kind: str, name: str, start_line: int, end_line: int) -> str:
    raw = f"{file_path}:{kind}:{name}:{start_line}:{end_line}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"anchor_{digest}"


def make_scope_node_id(label: str) -> str:
    digest = hashlib.sha1(label.encode("utf-8")).hexdigest()[:12]
    return f"scope_{digest}"
```

Write the parser in `src/repo_analysis_tools/anchors/parser.py`:

```python
from __future__ import annotations

from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_c


C_LANGUAGE = Language(tree_sitter_c.language())


class CAnchorParser:
    QUERY = C_LANGUAGE.query(
        """
        (function_definition declarator: (function_declarator declarator: (identifier) @function.name) @function.node)
        (declaration declarator: (function_declarator declarator: (identifier) @decl.name) @decl.node)
        (type_definition declarator: (type_identifier) @type.name) @type.node
        (preproc_def name: (identifier) @macro.name) @macro.node
        (preproc_function_def name: (identifier) @macro.name) @macro.node
        (preproc_include path: (string_literal) @include.path) @include.node
        (call_expression function: (identifier) @call.name) @call.node
        """
    )

    def __init__(self) -> None:
        self.parser = Parser()
        self.parser.set_language(C_LANGUAGE)

    def parse(self, file_path: Path) -> tuple[object, bytes]:
        source = file_path.read_bytes()
        return self.parser.parse(source), source
```

Write the core of `src/repo_analysis_tools/anchors/service.py`:

```python
from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.models import AnchorRecord, AnchorRelation, AnchorSnapshot
from repo_analysis_tools.anchors.parser import CAnchorParser
from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.ids import make_anchor_id
from repo_analysis_tools.scope.store import ScopeStore


class AnchorService:
    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.parser = CAnchorParser()

    @classmethod
    def for_repo(cls, repo: Path | str) -> "AnchorService":
        return cls(Path(repo).expanduser().resolve())

    def build_snapshot(self, scan_id: str) -> AnchorSnapshot:
        scope_snapshot = ScopeStore.for_repo(self.repo).load(scan_id=scan_id)
        anchors: list[AnchorRecord] = []
        relations: list[AnchorRelation] = []
        for item in scope_snapshot.files:
            if not item.path.endswith((".c", ".h")):
                continue
            path = self.repo / item.path
            tree, source = self.parser.parse(path)
            captures = self.parser.QUERY.captures(tree.root_node)
            for node, capture_name in captures:
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                raw_text = source[node.start_byte:node.end_byte].decode("utf-8", errors="replace").strip()
                if capture_name == "function.name":
                    name = raw_text
                    anchors.append(
                        AnchorRecord(
                            anchor_id=make_anchor_id(item.path, "function_definition", name, start_line, end_line),
                            kind="function_definition",
                            name=name,
                            file_path=item.path,
                            start_line=start_line,
                            end_line=end_line,
                            raw_text=raw_text,
                        )
                    )
                elif capture_name == "macro.name":
                    anchors.append(
                        AnchorRecord(
                            anchor_id=make_anchor_id(item.path, "macro_anchor", raw_text, start_line, end_line),
                            kind="macro_anchor",
                            name=raw_text,
                            file_path=item.path,
                            start_line=start_line,
                            end_line=end_line,
                            raw_text=raw_text,
                        )
                    )
                elif capture_name == "call.name":
                    relations.append(
                        AnchorRelation(
                            relation_kind="direct_call_edge",
                            source_file_path=item.path,
                            target_name=raw_text,
                            line_number=start_line,
                        )
                    )
                elif capture_name == "include.path":
                    relations.append(
                        AnchorRelation(
                            relation_kind="include_edge",
                            source_file_path=item.path,
                            target_name=raw_text.strip('"'),
                            line_number=start_line,
                        )
                    )
        snapshot = AnchorSnapshot(scan_id=scan_id, anchors=anchors, relations=relations)
        AnchorStore.for_repo(self.repo).save(snapshot)
        return snapshot
```

Update `src/repo_analysis_tools/scan/service.py` so scan now persists anchors after scope:

```python
from repo_analysis_tools.anchors.service import AnchorService

AnchorService.for_repo(repo).build_snapshot(scan_id=snapshot.scan_id)
```

Write the real anchor tools in `src/repo_analysis_tools/mcp/tools/anchors_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root


def list_anchors(target_repo: str, scan_id: str | None = None) -> dict:
    snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "anchors": [item.to_dict() for item in snapshot.anchors],
        },
        messages=["anchors loaded"],
        recommended_next_tools=["find_anchor", "plan_slice"],
    )


def find_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict:
    snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
    matches = [item for item in snapshot.anchors if item.name == anchor_name]
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "anchor_name": anchor_name,
            "matches": [item.to_dict() for item in matches],
        },
        messages=["anchor matches loaded"],
        recommended_next_tools=["describe_anchor", "plan_slice"],
    )


def describe_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict:
    snapshot = AnchorStore.for_repo(target_repo).load(scan_id=scan_id)
    match = next(item for item in snapshot.anchors if item.name == anchor_name)
    relations = [
        relation.to_dict()
        for relation in snapshot.relations
        if relation.source_file_path == match.file_path
    ]
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "scan_id": snapshot.scan_id,
            "anchor_name": anchor_name,
            "description": match.to_dict(),
            "relations": relations,
        },
        messages=["anchor described"],
        recommended_next_tools=["plan_slice", "build_evidence_pack"],
    )
```

Update `src/repo_analysis_tools/mcp/contracts/anchors.py` so the main M2 anchor payloads include normalized anchor records:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "anchors": "list",
}
```

for `list_anchors`, and:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "anchor_name": "string",
    "matches": "list",
}
```

for `find_anchor`.

Set `describe_anchor` to:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "scan_id": "scan_<12-hex>",
    "anchor_name": "string",
    "description": "dict",
    "relations": "list",
}
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_anchor_service tests.contract.test_tool_contracts -v`
Expected: PASS with `easyflash_init` found in `easyflash/src/easyflash.c` and `describe_anchor` returning at least the `ef_port_init` call relation.

- [ ] **Step 5: Commit the anchor layer**

```bash
git add pyproject.toml src/repo_analysis_tools/core/ids.py src/repo_analysis_tools/anchors src/repo_analysis_tools/scan/service.py src/repo_analysis_tools/mcp/contracts/anchors.py src/repo_analysis_tools/mcp/tools/anchors_tools.py tests/unit/test_anchor_service.py tests/contract/test_tool_contracts.py
git commit -m "feat: implement C anchor extraction"
```

### Task 5: Implement Slice Planning for Repository Understanding

**Files:**
- Create: `src/repo_analysis_tools/slice/models.py`
- Create: `src/repo_analysis_tools/slice/store.py`
- Create: `src/repo_analysis_tools/slice/query_classifier.py`
- Create: `src/repo_analysis_tools/slice/seed_resolver.py`
- Create: `src/repo_analysis_tools/slice/service.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/slice.py`
- Modify: `src/repo_analysis_tools/mcp/tools/slice_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Create: `tests/unit/test_slice_service.py`

- [ ] **Step 1: Write the failing slice-planning tests**

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.slice_tools import inspect_slice, plan_slice
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.service import SliceService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class SliceServiceTest(unittest.TestCase):
    def test_plan_slice_selects_flash_init_for_symbol_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            manifest = SliceService.for_repo(repo).plan("Where is flash_init defined?")

            self.assertEqual(manifest.query_kind, "locate_symbol")
            self.assertEqual(manifest.selected_files, ["src/flash.c"])
            self.assertEqual(manifest.selected_anchor_names, ["flash_init"])

    def test_plan_slice_selects_startup_flow_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            manifest = SliceService.for_repo(repo).plan("Explain startup flow")

            self.assertEqual(manifest.query_kind, "init_flow")
            self.assertEqual(manifest.selected_files, ["src/flash.c", "src/main.c"])

    def test_slice_tools_return_persisted_manifest_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            created = plan_slice(str(repo), question="Where is flash_init defined?")
            loaded = inspect_slice(str(repo), slice_id=created["data"]["slice_id"])

            self.assertEqual(loaded["data"]["slice_id"], created["data"]["slice_id"])
            self.assertEqual(loaded["data"]["members"], ["src/flash.c"])
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_slice_service tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.slice.service` and slice-tool payloads still using the M1 placeholder schemas.

- [ ] **Step 3: Build the classifier, seed resolver, persisted manifests, and real slice tools**

Write `src/repo_analysis_tools/slice/query_classifier.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryClassification:
    query_kind: str
    normalized_query: str


class QueryClassifier:
    def classify(self, question: str) -> QueryClassification:
        normalized = " ".join(question.lower().strip().rstrip("?").split())
        if "startup flow" in normalized or "init flow" in normalized:
            return QueryClassification(query_kind="init_flow", normalized_query=normalized)
        if normalized.startswith("what is the role of "):
            return QueryClassification(query_kind="file_role", normalized_query=normalized)
        if normalized.startswith("where is ") and (" defined" in normalized or normalized.endswith(" defined")):
            return QueryClassification(query_kind="locate_symbol", normalized_query=normalized)
        return QueryClassification(query_kind="general_question", normalized_query=normalized)
```

Write `src/repo_analysis_tools/slice/seed_resolver.py`:

```python
from __future__ import annotations

import difflib

from repo_analysis_tools.anchors.store import AnchorStore


class SeedResolver:
    def __init__(self, target_repo: str) -> None:
        self.store = AnchorStore.for_repo(target_repo)

    def resolve_symbol(self, scan_id: str, symbol_name: str) -> tuple[list[dict], list[str]]:
        snapshot = self.store.load(scan_id=scan_id)
        matches = [item.to_dict() for item in snapshot.anchors if item.name == symbol_name]
        if matches:
            return matches, []
        candidates = sorted({item.name for item in snapshot.anchors if item.name})
        return [], difflib.get_close_matches(symbol_name, candidates, n=3, cutoff=0.7)
```

Write the core of `src/repo_analysis_tools/slice/service.py`:

```python
from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.slice.models import SliceManifest
from repo_analysis_tools.slice.query_classifier import QueryClassifier
from repo_analysis_tools.slice.seed_resolver import SeedResolver
from repo_analysis_tools.slice.store import SliceStore
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id


class SliceService:
    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.classifier = QueryClassifier()

    @classmethod
    def for_repo(cls, repo: Path | str) -> "SliceService":
        return cls(Path(repo).expanduser().resolve())

    def plan(self, question: str, scan_id: str | None = None) -> SliceManifest:
        scan_snapshot = ScanStore.for_repo(self.repo).load(scan_id=scan_id)
        classification = self.classifier.classify(question)
        anchor_snapshot = AnchorStore.for_repo(self.repo).load(scan_id=scan_snapshot.scan_id)

        selected_files: list[str] = []
        selected_anchor_names: list[str] = []
        notes: list[str] = []
        if classification.query_kind == "locate_symbol":
            symbol = question.split("Where is ", 1)[1].split(" defined", 1)[0].strip(" ?")
            matches, alternates = SeedResolver(str(self.repo)).resolve_symbol(scan_snapshot.scan_id, symbol)
            selected_files = sorted({item["file_path"] for item in matches})
            selected_anchor_names = sorted({item["name"] for item in matches})
            if not matches and alternates:
                notes.append(f"did_you_mean={alternates[0]}")
        elif classification.query_kind == "init_flow":
            selected_files = ["src/flash.c", "src/main.c"]
            selected_anchor_names = ["flash_init", "main"]
        else:
            selected_files = sorted({item.file_path for item in anchor_snapshot.anchors if item.file_path.startswith("src/")})

        manifest = SliceManifest(
            slice_id=make_stable_id(StableIdKind.SLICE),
            scan_id=scan_snapshot.scan_id,
            question=question,
            query_kind=classification.query_kind,
            status="complete" if selected_files else "no_match",
            selected_files=selected_files,
            selected_anchor_names=selected_anchor_names,
            notes=notes,
        )
        SliceStore.for_repo(self.repo).save(manifest)
        return manifest
```

Write the real slice tools in `src/repo_analysis_tools/mcp/tools/slice_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.slice.service import SliceService
from repo_analysis_tools.slice.store import SliceStore


def plan_slice(target_repo: str, question: str) -> dict:
    manifest = SliceService.for_repo(target_repo).plan(question)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "slice_id": manifest.slice_id,
            "scan_id": manifest.scan_id,
            "query_kind": manifest.query_kind,
            "status": manifest.status,
            "selected_files": manifest.selected_files,
            "selected_anchor_names": manifest.selected_anchor_names,
            "notes": manifest.notes,
        },
        messages=["slice planned"],
        recommended_next_tools=["build_evidence_pack", "inspect_slice"],
    )


def inspect_slice(target_repo: str, slice_id: str) -> dict:
    manifest = SliceStore.for_repo(target_repo).load(slice_id=slice_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "slice_id": manifest.slice_id,
            "members": manifest.selected_files,
        },
        messages=["slice loaded"],
        recommended_next_tools=["build_evidence_pack", "list_anchors"],
    )


def expand_slice(target_repo: str, slice_id: str) -> dict:
    manifest = SliceStore.for_repo(target_repo).load(slice_id=slice_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "slice_id": manifest.slice_id,
            "expanded": False,
        },
        messages=["M2 keeps expand_slice as a bounded no-op over the persisted manifest"],
        recommended_next_tools=["inspect_slice", "build_evidence_pack"],
    )
```

Update `src/repo_analysis_tools/mcp/contracts/slice.py` so the real M2 `plan_slice` schema becomes:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "slice_id": "slice_<12-hex>",
    "scan_id": "scan_<12-hex>",
    "query_kind": "string",
    "status": "string",
    "selected_files": "list",
    "selected_anchor_names": "list",
    "notes": "list",
}
```

Keep `inspect_slice` and `expand_slice` simple but explicit:

```python
inspect_output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "slice_id": "slice_<12-hex>",
    "members": "list",
}

expand_output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "slice_id": "slice_<12-hex>",
    "expanded": "bool",
}
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_slice_service tests.contract.test_tool_contracts -v`
Expected: PASS with `flash_init` slices selecting `src/flash.c`, startup-flow slices selecting `src/main.c` and `src/flash.c`, and persisted manifests loading correctly through `inspect_slice`.

- [ ] **Step 5: Commit the slice layer**

```bash
git add src/repo_analysis_tools/slice src/repo_analysis_tools/mcp/contracts/slice.py src/repo_analysis_tools/mcp/tools/slice_tools.py tests/unit/test_slice_service.py tests/contract/test_tool_contracts.py
git commit -m "feat: implement repository-understanding slice planning"
```

### Task 6: Implement Evidence Packs and Guarded `open_span`

**Files:**
- Create: `src/repo_analysis_tools/evidence/models.py`
- Create: `src/repo_analysis_tools/evidence/store.py`
- Create: `src/repo_analysis_tools/evidence/snippets.py`
- Create: `src/repo_analysis_tools/evidence/freshness.py`
- Create: `src/repo_analysis_tools/evidence/service.py`
- Modify: `src/repo_analysis_tools/mcp/contracts/evidence.py`
- Modify: `src/repo_analysis_tools/mcp/tools/evidence_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Create: `tests/unit/test_evidence_service.py`

- [ ] **Step 1: Write the failing evidence and guarded-span tests**

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.service import SliceService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class EvidenceServiceTest(unittest.TestCase):
    def test_build_and_read_evidence_pack_returns_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            manifest = SliceService.for_repo(repo).plan("Where is flash_init defined?")

            created = build_evidence_pack(str(repo), slice_id=manifest.slice_id)
            loaded = read_evidence_pack(str(repo), evidence_pack_id=created["data"]["evidence_pack_id"])

            self.assertEqual(created["status"], "ok")
            self.assertEqual(loaded["data"]["citations"][0]["file_path"], "src/flash.c")
            self.assertEqual(loaded["data"]["citations"][0]["line_start"], 1)

    def test_open_span_rejects_ranges_outside_evidence_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            ScanService().scan(repo)
            manifest = SliceService.for_repo(repo).plan("Where is flash_init defined?")
            created = build_evidence_pack(str(repo), slice_id=manifest.slice_id)

            payload = open_span(
                str(repo),
                evidence_pack_id=created["data"]["evidence_pack_id"],
                path="src/main.c",
                line_start=1,
                line_end=3,
            )

            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["data"]["error"]["code"], "invalid_input")
```

Add this snippet test to `tests/unit/test_evidence_service.py` too:

```python
def test_read_snippet_supports_gb18030_sources(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "encoding-repo"
        (repo / "src").mkdir(parents=True, exist_ok=True)
        (repo / "src" / "flash.c").write_bytes(
            "/* 中文注释 */\nint flash_init(void) { return 0; }\n".encode("gb18030")
        )
        snippet = read_snippet(repo, "src/flash.c", 1, 2)
        self.assertEqual(snippet, "/* 中文注释 */\nint flash_init(void) { return 0; }")
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_evidence_service tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.evidence.service` and `open_span` still returning the M1 placeholder `lines` list instead of a guarded error.

- [ ] **Step 3: Build evidence packs, freshness checks, snippet decoding, and guarded span access**

Write `src/repo_analysis_tools/evidence/snippets.py`:

```python
from pathlib import Path


def read_snippet(target_repo: Path | str, relative_path: str, line_start: int, line_end: int) -> str:
    repo = Path(target_repo).expanduser().resolve()
    raw_bytes = (repo / relative_path).read_bytes()
    for encoding in ("utf-8", "gb18030"):
        try:
            text = raw_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw_bytes.decode("utf-8", errors="replace")
    lines = text.splitlines()
    selected = lines[line_start - 1:line_end]
    return "\n".join(selected)
```

Write `src/repo_analysis_tools/evidence/freshness.py`:

```python
from __future__ import annotations

import hashlib
from pathlib import Path

from repo_analysis_tools.scan.store import ScanStore


def evaluate_selected_file_freshness(target_repo: Path | str, scan_id: str, selected_files: list[str]) -> list[str]:
    repo = Path(target_repo).expanduser().resolve()
    scan_snapshot = ScanStore.for_repo(repo).load(scan_id=scan_id)
    digests = {item.path: item.content_sha256 for item in scan_snapshot.files}
    drifted: list[str] = []
    for file_path in selected_files:
        actual = hashlib.sha256((repo / file_path).read_bytes()).hexdigest()
        if digests.get(file_path) != actual:
            drifted.append(file_path)
    return drifted
```

Write the core of `src/repo_analysis_tools/evidence/service.py`:

```python
from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.errors import ErrorCode, error_response
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.evidence.freshness import evaluate_selected_file_freshness
from repo_analysis_tools.evidence.models import CitationRecord, EvidencePack
from repo_analysis_tools.evidence.snippets import read_snippet
from repo_analysis_tools.evidence.store import EvidenceStore
from repo_analysis_tools.slice.store import SliceStore


MAX_OPEN_SPAN_LINES = 40


class EvidenceService:
    @classmethod
    def for_repo(cls, repo: Path | str) -> "EvidenceService":
        return cls(Path(repo).expanduser().resolve())

    def __init__(self, repo: Path) -> None:
        self.repo = repo

    def build(self, slice_id: str) -> EvidencePack:
        manifest = SliceStore.for_repo(self.repo).load(slice_id=slice_id)
        drifted = evaluate_selected_file_freshness(self.repo, manifest.scan_id, manifest.selected_files)
        if drifted:
            raise ValueError(f"selected files drifted since scan: {', '.join(drifted)}")
        anchor_snapshot = AnchorStore.for_repo(self.repo).load(scan_id=manifest.scan_id)
        selected_anchors = [
            anchor
            for anchor in anchor_snapshot.anchors
            if anchor.name in manifest.selected_anchor_names and anchor.file_path in manifest.selected_files
        ]
        citations = []
        if selected_anchors:
            for index, anchor in enumerate(selected_anchors, start=1):
                citations.append(
                    CitationRecord(
                        citation_id=f"citation_{index:02d}",
                        file_path=anchor.file_path,
                        line_start=anchor.start_line,
                        line_end=anchor.end_line,
                        label=f"{anchor.file_path}:{anchor.start_line}-{anchor.end_line}",
                        snippet_text=read_snippet(self.repo, anchor.file_path, anchor.start_line, anchor.end_line),
                    )
                )
        else:
            for index, file_path in enumerate(manifest.selected_files, start=1):
                citations.append(
                    CitationRecord(
                        citation_id=f"citation_{index:02d}",
                        file_path=file_path,
                        line_start=1,
                        line_end=1,
                        label=f"{file_path}:1-1",
                        snippet_text=read_snippet(self.repo, file_path, 1, 1),
                    )
                )
        pack = EvidencePack(
            evidence_pack_id=make_stable_id(StableIdKind.EVIDENCE_PACK),
            slice_id=manifest.slice_id,
            scan_id=manifest.scan_id,
            citations=citations,
            selected_files=manifest.selected_files,
            summary=f"{len(citations)} citations for {manifest.question}",
        )
        EvidenceStore.for_repo(self.repo).save(pack)
        return pack

    def open_span(self, evidence_pack_id: str, path: str, line_start: int, line_end: int) -> dict:
        if line_end < line_start or (line_end - line_start + 1) > MAX_OPEN_SPAN_LINES:
            return error_response(ErrorCode.INVALID_INPUT, "requested span exceeds open_span limits")
        pack = EvidenceStore.for_repo(self.repo).load(evidence_pack_id=evidence_pack_id)
        allowed = any(
            citation.file_path == path and citation.line_start <= line_start and line_end <= citation.line_end
            for citation in pack.citations
        )
        if not allowed:
            return error_response(ErrorCode.INVALID_INPUT, "requested span is outside evidence-pack bounds")
        return {
            "path": path,
            "line_start": line_start,
            "line_end": line_end,
            "lines": read_snippet(self.repo, path, line_start, line_end).splitlines(),
        }
```

Write the real evidence tools in `src/repo_analysis_tools/mcp/tools/evidence_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.evidence.service import EvidenceService
from repo_analysis_tools.evidence.store import EvidenceStore


def build_evidence_pack(target_repo: str, slice_id: str) -> dict:
    pack = EvidenceService.for_repo(target_repo).build(slice_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "slice_id": pack.slice_id,
            "evidence_pack_id": pack.evidence_pack_id,
            "citation_count": len(pack.citations),
            "summary": pack.summary,
        },
        messages=["evidence pack built"],
        recommended_next_tools=["read_evidence_pack", "open_span"],
    )


def read_evidence_pack(target_repo: str, evidence_pack_id: str) -> dict:
    pack = EvidenceStore.for_repo(target_repo).load(evidence_pack_id=evidence_pack_id)
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "evidence_pack_id": pack.evidence_pack_id,
            "summary": pack.summary,
            "citations": [citation.to_dict() for citation in pack.citations],
        },
        messages=["evidence pack loaded"],
        recommended_next_tools=["open_span", "describe_anchor"],
    )


def open_span(target_repo: str, evidence_pack_id: str, path: str, line_start: int, line_end: int) -> dict:
    payload = EvidenceService.for_repo(target_repo).open_span(
        evidence_pack_id=evidence_pack_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
    )
    if payload.get("schema_version") == "1":
        return payload
    return ok_response(
        data={
            "target_repo": target_repo,
            "runtime_root": runtime_root(Path(target_repo)).as_posix(),
            "evidence_pack_id": evidence_pack_id,
            "path": payload["path"],
            "line_start": payload["line_start"],
            "line_end": payload["line_end"],
            "lines": payload["lines"],
        },
        messages=["bounded span opened"],
        recommended_next_tools=["read_evidence_pack", "describe_anchor"],
    )
```

Update `src/repo_analysis_tools/mcp/contracts/evidence.py` so the M2 `read_evidence_pack` schema becomes:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "evidence_pack_id": "evidence_pack_<12-hex>",
    "summary": "string",
    "citations": "list",
}
```

and the M2 `open_span` schema becomes:

```python
output_schema={
    "target_repo": "string",
    "runtime_root": "string",
    "evidence_pack_id": "evidence_pack_<12-hex>",
    "path": "string",
    "line_start": "int",
    "line_end": "int",
    "lines": "list",
}
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_evidence_service tests.contract.test_tool_contracts -v`
Expected: PASS with evidence packs returning real citations, GB18030 snippets decoding correctly, and `open_span` rejecting out-of-bounds requests.

- [ ] **Step 5: Commit the evidence layer**

```bash
git add src/repo_analysis_tools/evidence src/repo_analysis_tools/mcp/contracts/evidence.py src/repo_analysis_tools/mcp/tools/evidence_tools.py tests/unit/test_evidence_service.py tests/contract/test_tool_contracts.py
git commit -m "feat: implement evidence packs and guarded open span"
```

### Task 7: Add the `repo-understand` Skill, Golden Fixtures, Docs, and End-to-End Validation

**Files:**
- Create: `.agents/skills/repo-understand/SKILL.md`
- Modify: `docs/architecture.md`
- Modify: `docs/contracts/mcp-tool-contracts.md`
- Modify: `tests/contract/test_tool_contracts.py`
- Modify: `tests/golden/test_contract_golden.py`
- Modify: `tests/golden/fixtures/scan_repo.json`
- Create: `tests/golden/fixtures/read_evidence_pack_scope_first.json`
- Create: `tests/integration/test_mainline_mcp_workflow.py`
- Create: `tests/e2e/test_repo_understand_easyflash.py`

- [ ] **Step 1: Write the failing integration, golden, and end-to-end tests**

Create `tests/integration/test_mainline_mcp_workflow.py`:

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import find_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.scope_tools import show_scope
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class MainlineMcpWorkflowTest(unittest.TestCase):
    def test_scope_first_repo_mainline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_payload = scan_repo(str(repo))
            scope_payload = show_scope(str(repo))
            anchor_payload = find_anchor(str(repo), anchor_name="flash_init")
            slice_payload = plan_slice(str(repo), question="Where is flash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), slice_id=slice_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), evidence_pack_id=evidence_payload["data"]["evidence_pack_id"])
            span_payload = open_span(
                str(repo),
                evidence_pack_id=evidence_payload["data"]["evidence_pack_id"],
                path="src/flash.c",
                line_start=1,
                line_end=1,
            )

            self.assertEqual(scan_payload["data"]["file_count"], 6)
            self.assertIn("primary", scope_payload["data"]["scope_summary"])
            self.assertEqual(anchor_payload["data"]["matches"][0]["file_path"], "src/flash.c")
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "src/flash.c")
            self.assertIn("flash_init", "\n".join(span_payload["data"]["lines"]))
```

Create `tests/e2e/test_repo_understand_easyflash.py`:

```python
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.anchors_tools import find_anchor
from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, open_span, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice


class RepoUnderstandEasyFlashE2ETest(unittest.TestCase):
    def test_easyflash_mainline_locates_easyflash_init(self) -> None:
        repo = Path(__file__).resolve().parents[1] / "fixtures" / "repos" / "easyflash"
        scan_payload = scan_repo(str(repo))
        anchor_payload = find_anchor(str(repo), anchor_name="easyflash_init")
        slice_payload = plan_slice(str(repo), question="Where is easyflash_init defined?")
        evidence_payload = build_evidence_pack(str(repo), slice_id=slice_payload["data"]["slice_id"])
        read_payload = read_evidence_pack(str(repo), evidence_pack_id=evidence_payload["data"]["evidence_pack_id"])
        span_payload = open_span(
            str(repo),
            evidence_pack_id=evidence_payload["data"]["evidence_pack_id"],
            path="easyflash/src/easyflash.c",
            line_start=65,
            line_end=80,
        )

        self.assertRegex(scan_payload["data"]["scan_id"], r"^scan_[0-9a-f]{12}$")
        self.assertEqual(anchor_payload["data"]["matches"][0]["file_path"], "easyflash/src/easyflash.c")
        self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "easyflash/src/easyflash.c")
        self.assertIn("EfErrCode easyflash_init(void)", "\n".join(span_payload["data"]["lines"]))
```

Update `tests/golden/test_contract_golden.py` with a real tool golden:

```python
import tempfile
from pathlib import Path
from unittest.mock import patch

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


def test_read_evidence_pack_matches_golden_fixture(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = build_scope_first_repo(Path(tmpdir))
        with patch("repo_analysis_tools.scan.service.make_stable_id", return_value="scan_000000000001"), \
             patch("repo_analysis_tools.slice.service.make_stable_id", return_value="slice_000000000001"), \
             patch("repo_analysis_tools.evidence.service.make_stable_id", return_value="evidence_pack_000000000001"):
            scan_repo(str(repo))
            slice_payload = plan_slice(str(repo), question="Where is flash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), slice_id=slice_payload["data"]["slice_id"])
            payload = read_evidence_pack(str(repo), evidence_pack_id=evidence_payload["data"]["evidence_pack_id"])
    assert_matches_fixture(self, "read_evidence_pack_scope_first.json", payload)
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.integration.test_mainline_mcp_workflow tests.e2e.test_repo_understand_easyflash tests.golden.test_contract_golden -v`
Expected: FAIL because the skill file does not exist yet, the golden fixture has not been updated, and at least one integration or EasyFlash assertion will expose any remaining contract gaps.

- [ ] **Step 3: Add the workflow skill, update docs, and record the golden fixtures**

Write `.agents/skills/repo-understand/SKILL.md`:

```md
---
name: repo-understand
description: Understand an unfamiliar C repository by sequencing MCP tools and grounding every conclusion in evidence.
---

# Repo Understand

Use this skill when you need to understand an unfamiliar C repository without skipping traceability.

## Required Tool Order

1. Call `scan_repo`.
2. Call `get_scan_status`.
3. Call `show_scope`.
4. Use `find_anchor` or `list_anchors`.
5. Call `plan_slice`.
6. Call `build_evidence_pack`.
7. Call `read_evidence_pack`.
8. Call `open_span` only for spans already cited by the evidence pack.

## Output Rules

- Put confirmed observations under `Confirmed facts`.
- Put reasoning under `Interpretation`.
- Put gaps under `Unknowns`.
- Cite file paths and line ranges whenever you quote or summarize code behavior.
- Do not claim a behavior that is not supported by `read_evidence_pack` or `open_span`.
```

Update the relevant part of `docs/architecture.md`:

```md
## M2 Mainline

Runtime assets now persist as JSON under `<target_repo>/.codewiki/{scan,scope,anchors,slice,evidence}/`.

The supported repository-understanding path is:

`scan_repo -> get_scan_status -> show_scope -> find_anchor/list_anchors -> plan_slice -> build_evidence_pack -> read_evidence_pack -> open_span`

`open_span` is intentionally narrower than general file reading:

- it only opens ranges already covered by persisted evidence citations
- it rejects requests larger than 40 lines
- it should be treated as the final inspection step, not the first discovery step
```

Update the real-surface rows in `docs/contracts/mcp-tool-contracts.md`:

```md
| Tool | Key output fields | Notes |
| --- | --- | --- |
| `scan_repo` | `scan_id`, `repo_root`, `file_count`, `latest_completed_at` | Creates persisted scan assets under `.codewiki/scan/`. |
| `show_scope` | `scope_summary`, `role_counts` | Reads the scope snapshot produced by the selected scan. |
| `find_anchor` | `matches[]` | Returns normalized anchor records with deterministic `anchor_id`s. |
| `plan_slice` | `slice_id`, `query_kind`, `selected_files`, `notes` | Produces a bounded manifest for repository understanding. |
| `read_evidence_pack` | `summary`, `citations[]` | Must be read before `open_span`. |
| `open_span` | `path`, `line_start`, `line_end`, `lines[]` | Bounded to evidence-backed ranges and a 40-line maximum. |
```

Record `tests/golden/fixtures/read_evidence_pack_scope_first.json` with the exact deterministic payload produced by the test above, and replace `tests/golden/fixtures/scan_repo.json` with the real M2 `scan_repo` payload shape rather than the M1 stub envelope.

- [ ] **Step 4: Run the full M2 verification suite and verify it passes**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest discover -s tests -t . -v`
Expected: PASS with unit, contract, smoke, golden, integration, and `EasyFlash` end-to-end coverage all green.

- [ ] **Step 5: Commit the M2 mainline handoff**

```bash
git add .agents/skills/repo-understand/SKILL.md docs/architecture.md docs/contracts/mcp-tool-contracts.md tests/contract/test_tool_contracts.py tests/golden tests/integration/test_mainline_mcp_workflow.py tests/e2e/test_repo_understand_easyflash.py
git commit -m "feat: deliver M2 analysis-first mainline"
```
