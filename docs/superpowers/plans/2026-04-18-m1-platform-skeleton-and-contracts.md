# M1 Platform Skeleton and Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first runnable version of the new repository with visible package boundaries, `.codewiki/` runtime conventions, stable MCP response contracts, domain tool stubs, and structural tests that let M2 add real analysis logic without reopening the skeleton.

**Architecture:** Build M1 from the outside in. First create the Python project shell and all required top-level directories, then lock the shared runtime primitives for IDs, paths, errors, and storage ownership, then define the MCP contract catalog and stub tool implementations for every required domain. Finish by wiring a minimal stdio MCP server, adding contract and golden tests, and writing architecture-facing documentation that mirrors the code-level rules.

**Tech Stack:** Python 3.11 (`/home/hyx/anaconda3/envs/agent/bin/python`), stdlib `unittest`, official MCP Python SDK (`mcp[cli]`), Hatchling, Markdown docs

---

## File Structure

- Create: `pyproject.toml`
  Responsibility: package metadata and runtime dependency on the MCP SDK. Task 4 extends it with the stdio server console script after the server entrypoint exists.
- Create: `README.md`
  Responsibility: short repository overview stating that M1 is a contract-first skeleton and that runtime artifacts live under `.codewiki/`.
- Create: `src/repo_analysis_tools/__init__.py`
  Responsibility: root package marker and version export.
- Create directories: `src/repo_analysis_tools/core`, `storage`, `scan`, `scope`, `anchors`, `slice`, `evidence`, `impact`, `report`, `export`, `mcp`, `skills`, `doc_specs`, `doc_dsl`, `renderers`
  Responsibility: make every required top-level boundary visible before real implementation begins.
- Create: `src/repo_analysis_tools/core/ids.py`
  Responsibility: stable ID kinds and helpers for scans, slices, evidence packs, reports, and exports.
- Create: `src/repo_analysis_tools/core/paths.py`
  Responsibility: `.codewiki/` runtime root and repository-relative path normalization rules.
- Create: `src/repo_analysis_tools/core/errors.py`
  Responsibility: MCP-facing error taxonomy and the shared response envelope helpers.
- Create: `src/repo_analysis_tools/storage/contracts.py`
  Responsibility: explicit per-domain storage ownership under `.codewiki/`.
- Create: `src/repo_analysis_tools/mcp/contracts/common.py`
  Responsibility: shared dataclass for tool contracts.
- Create: `src/repo_analysis_tools/mcp/contracts/__init__.py`
  Responsibility: aggregated domain contract registry and tool lookup table.
- Create: `src/repo_analysis_tools/mcp/contracts/scan.py`, `scope.py`, `anchors.py`, `slice.py`, `evidence.py`, `impact.py`, `report.py`, `export.py`
  Responsibility: per-domain tool contracts with input shape, output shape, stable IDs, failure modes, and recommended next tools.
- Create: `src/repo_analysis_tools/mcp/tools/shared.py`
  Responsibility: shared stub response builder that enforces the common MCP envelope.
- Create: `src/repo_analysis_tools/mcp/tools/__init__.py`
  Responsibility: import all tool modules for registration side effects.
- Create: `src/repo_analysis_tools/mcp/tools/scan_tools.py`, `scope_tools.py`, `anchors_tools.py`, `slice_tools.py`, `evidence_tools.py`, `impact_tools.py`, `report_tools.py`, `export_tools.py`
  Responsibility: FastMCP tool stubs for every required domain group.
- Create: `src/repo_analysis_tools/mcp/app.py`
  Responsibility: FastMCP application object configured for JSON responses.
- Create: `src/repo_analysis_tools/mcp/server.py`
  Responsibility: stdio entrypoint that imports and registers all tool stubs.
- Create: `docs/architecture.md`
  Responsibility: architecture-facing summary of package boundaries, runtime rules, and storage ownership.
- Create: `docs/contracts/mcp-tool-contracts.md`
  Responsibility: human-readable contract table matching the code-level MCP registry.
- Create: `tests/__init__.py`
  Responsibility: add `src/` to `sys.path` for zero-install local test execution.
- Create: `tests/smoke/__init__.py`, `tests/unit/__init__.py`, `tests/contract/__init__.py`, `tests/golden/__init__.py`
  Responsibility: make the test directories importable for `/home/hyx/anaconda3/envs/agent/bin/python -m unittest ...`.
- Create: `tests/smoke/test_package_layout.py`
  Responsibility: verify the root package and all required top-level directories exist.
- Create: `tests/unit/test_runtime_contracts.py`
  Responsibility: verify `.codewiki/`, stable ID prefixes, normalized paths, and storage ownership.
- Create: `tests/contract/test_tool_contracts.py`
  Responsibility: verify the domain contract registry and shared MCP response envelope.
- Create: `tests/smoke/test_mcp_server.py`
  Responsibility: prove the stdio MCP server process starts successfully.
- Create: `tests/golden/harness.py`
  Responsibility: tiny fixture loader for later contract snapshots.
- Create: `tests/golden/fixtures/scan_repo.json`
  Responsibility: starter golden artifact for one MCP contract stub.
- Create: `tests/golden/test_contract_golden.py`
  Responsibility: verify deterministic contract output matches the starter golden file.
- Create: `tests/unit/test_architecture_docs.py`
  Responsibility: verify the architecture and contract docs mention the rules that M1 must freeze.

## Working Set

- Parent design: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- M1 spec: `docs/superpowers/specs/2026-04-17-m1-platform-skeleton-and-contracts-spec.md`
- Existing plan style reference: `docs/superpowers/plans/2026-04-18-m0-old-repo-harvest.md`
- MCP SDK reference: `https://py.sdk.modelcontextprotocol.io/`
- Python runtime for this machine: `/home/hyx/anaconda3/envs/agent/bin/python`

### Task 1: Bootstrap the Repository Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/repo_analysis_tools/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/smoke/__init__.py`
- Create: `tests/smoke/test_package_layout.py`
- Create placeholder files: `src/repo_analysis_tools/core/.gitkeep`, `storage/.gitkeep`, `scan/.gitkeep`, `scope/.gitkeep`, `anchors/.gitkeep`, `slice/.gitkeep`, `evidence/.gitkeep`, `impact/.gitkeep`, `report/.gitkeep`, `export/.gitkeep`, `mcp/.gitkeep`, `skills/.gitkeep`, `doc_specs/.gitkeep`, `doc_dsl/.gitkeep`, `renderers/.gitkeep`
- Create placeholder files: `tests/unit/.gitkeep`, `tests/contract/.gitkeep`, `tests/golden/fixtures/.gitkeep`
- Create placeholder file: `docs/contracts/.gitkeep`

- [ ] **Step 1: Write the failing skeleton test**

```python
import unittest
from pathlib import Path

import repo_analysis_tools


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DIRECTORIES = [
    ROOT / "src" / "repo_analysis_tools" / "core",
    ROOT / "src" / "repo_analysis_tools" / "storage",
    ROOT / "src" / "repo_analysis_tools" / "scan",
    ROOT / "src" / "repo_analysis_tools" / "scope",
    ROOT / "src" / "repo_analysis_tools" / "anchors",
    ROOT / "src" / "repo_analysis_tools" / "slice",
    ROOT / "src" / "repo_analysis_tools" / "evidence",
    ROOT / "src" / "repo_analysis_tools" / "impact",
    ROOT / "src" / "repo_analysis_tools" / "report",
    ROOT / "src" / "repo_analysis_tools" / "export",
    ROOT / "src" / "repo_analysis_tools" / "mcp",
    ROOT / "src" / "repo_analysis_tools" / "skills",
    ROOT / "src" / "repo_analysis_tools" / "doc_specs",
    ROOT / "src" / "repo_analysis_tools" / "doc_dsl",
    ROOT / "src" / "repo_analysis_tools" / "renderers",
]


class PackageLayoutTest(unittest.TestCase):
    def test_root_package_imports(self) -> None:
        self.assertEqual(repo_analysis_tools.__version__, "0.1.0")

    def test_required_top_level_directories_exist(self) -> None:
        for path in EXPECTED_DIRECTORIES:
            self.assertTrue(path.is_dir(), str(path))
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.smoke.test_package_layout -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'repo_analysis_tools'`

- [ ] **Step 3: Write the minimal project skeleton**

Create the directories and trackable placeholders first:

```bash
mkdir -p src/repo_analysis_tools/{core,storage,scan,scope,anchors,slice,evidence,impact,report,export,mcp,skills,doc_specs,doc_dsl,renderers}
mkdir -p tests/{smoke,unit,contract,golden/fixtures}
mkdir -p docs/contracts
touch src/repo_analysis_tools/{core,storage,scan,scope,anchors,slice,evidence,impact,report,export,mcp,skills,doc_specs,doc_dsl,renderers}/.gitkeep
touch tests/unit/.gitkeep tests/contract/.gitkeep tests/golden/fixtures/.gitkeep docs/contracts/.gitkeep
```

Write `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "repo-analysis-tools"
version = "0.1.0"
description = "MCP-first repository analysis platform"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "mcp[cli]>=1.0,<2.0",
]

```

Write `README.md`:

```md
# Repo Analysis Tools

M1 establishes the platform skeleton, MCP contracts, and runtime boundaries for the new repository analysis platform.

All per-target runtime artifacts live under `<target_repo>/.codewiki/`.
```

Write `src/repo_analysis_tools/__init__.py`:

```python
"""Root package for the repository analysis platform."""

__all__ = ["__version__"]

__version__ = "0.1.0"
```

Write `tests/__init__.py`:

```python
from pathlib import Path
import sys


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
```

Write `tests/smoke/__init__.py`:

```python
"""Smoke tests for repo-analysis-tools."""
```

- [ ] **Step 4: Install the MCP SDK dependency**

Install the MCP dependency that later tasks rely on:

```bash
/home/hyx/anaconda3/envs/agent/bin/python -m pip install "mcp[cli]>=1.0,<2.0"
```

- [ ] **Step 5: Run the skeleton test and verify it passes**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.smoke.test_package_layout -v`
Expected: PASS with `test_root_package_imports` and `test_required_top_level_directories_exist`

- [ ] **Step 6: Commit the bootstrap**

```bash
git add pyproject.toml README.md src tests docs/contracts/.gitkeep
git commit -m "feat: bootstrap M1 repository skeleton"
```

### Task 2: Lock Runtime, ID, Error, and Storage Contracts

**Files:**
- Create: `src/repo_analysis_tools/core/ids.py`
- Create: `src/repo_analysis_tools/core/paths.py`
- Create: `src/repo_analysis_tools/core/errors.py`
- Create: `src/repo_analysis_tools/storage/contracts.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_runtime_contracts.py`

- [ ] **Step 1: Write the failing runtime contract tests**

```python
import unittest
from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import (
    domain_storage_root,
    normalize_repo_relative_path,
    runtime_root,
)
from repo_analysis_tools.storage.contracts import STORAGE_BOUNDARIES


class RuntimeContractsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path("/tmp/example-repo")

    def test_runtime_root_is_codewiki(self) -> None:
        self.assertEqual(runtime_root(self.repo_root), self.repo_root / ".codewiki")

    def test_normalize_repo_relative_path_rejects_escape(self) -> None:
        with self.assertRaises(ValueError):
            normalize_repo_relative_path(self.repo_root, "../outside.c")

    def test_make_stable_id_uses_expected_prefix(self) -> None:
        self.assertTrue(make_stable_id(StableIdKind.SCAN).startswith("scan_"))
        self.assertTrue(make_stable_id(StableIdKind.SLICE).startswith("slice_"))

    def test_error_response_preserves_mcp_envelope_shape(self) -> None:
        payload = error_response(ErrorCode.INVALID_INPUT, "bad input")
        self.assertEqual(
            set(payload),
            {"schema_version", "status", "data", "messages", "recommended_next_tools"},
        )
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"]["error"]["code"], "invalid_input")

    def test_storage_boundaries_live_under_runtime_root(self) -> None:
        self.assertEqual(domain_storage_root(self.repo_root, "scan"), self.repo_root / ".codewiki" / "scan")
        self.assertEqual(STORAGE_BOUNDARIES["evidence"].directory_name, "evidence")
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_runtime_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.core.errors`

- [ ] **Step 3: Write the shared runtime contract modules**

Write `tests/unit/__init__.py`:

```python
"""Unit tests for repo-analysis-tools."""
```

Write `src/repo_analysis_tools/core/ids.py`:

```python
from enum import StrEnum
import uuid


class StableIdKind(StrEnum):
    SCAN = "scan"
    SLICE = "slice"
    EVIDENCE_PACK = "evidence_pack"
    REPORT = "report"
    EXPORT = "export"


def make_stable_id(kind: StableIdKind) -> str:
    return f"{kind.value}_{uuid.uuid4().hex[:12]}"
```

Write `src/repo_analysis_tools/core/paths.py`:

```python
from pathlib import Path


RUNTIME_DIRNAME = ".codewiki"


def runtime_root(target_repo: Path | str) -> Path:
    return Path(target_repo).expanduser() / RUNTIME_DIRNAME


def normalize_repo_relative_path(target_repo: Path | str, candidate: Path | str) -> str:
    repo_root = Path(target_repo).resolve()
    raw_path = Path(candidate)
    absolute_path = raw_path.resolve() if raw_path.is_absolute() else (repo_root / raw_path).resolve()
    try:
        relative_path = absolute_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"{candidate!s} escapes repository root {repo_root}") from exc
    return relative_path.as_posix()


def domain_storage_root(target_repo: Path | str, domain_name: str) -> Path:
    return runtime_root(target_repo) / domain_name
```

Write `src/repo_analysis_tools/core/errors.py`:

```python
from enum import StrEnum
from typing import Any


SCHEMA_VERSION = "1"


class ErrorCode(StrEnum):
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RUNTIME_STATE = "runtime_state"
    INTERNAL = "internal"


def _message(level: str, text: str) -> dict[str, str]:
    return {"level": level, "text": text}


def ok_response(
    *,
    data: dict[str, Any],
    messages: list[str] | None = None,
    recommended_next_tools: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ok",
        "data": data,
        "messages": [_message("info", text) for text in (messages or [])],
        "recommended_next_tools": recommended_next_tools or [],
    }


def error_response(
    code: ErrorCode,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    recommended_next_tools: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "data": {
            "error": {
                "code": code.value,
                "message": message,
                "details": details or {},
            }
        },
        "messages": [_message("error", message)],
        "recommended_next_tools": recommended_next_tools or [],
    }
```

Write `src/repo_analysis_tools/storage/contracts.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StorageBoundary:
    domain: str
    directory_name: str
    owner_description: str


STORAGE_BOUNDARIES = {
    "scan": StorageBoundary("scan", "scan", "scan metadata and scan handles"),
    "scope": StorageBoundary("scope", "scope", "scope snapshots derived from scans"),
    "anchors": StorageBoundary("anchors", "anchors", "anchor extraction outputs"),
    "slice": StorageBoundary("slice", "slice", "slice manifests and expansions"),
    "evidence": StorageBoundary("evidence", "evidence", "evidence packs and citations"),
    "impact": StorageBoundary("impact", "impact", "impact analysis artifacts"),
    "report": StorageBoundary("report", "report", "report payloads before export"),
    "export": StorageBoundary("export", "export", "exported analysis bundles"),
}
```

- [ ] **Step 4: Run the runtime contract tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_runtime_contracts -v`
Expected: PASS with five tests covering `.codewiki`, path normalization, stable IDs, error envelopes, and storage roots

- [ ] **Step 5: Commit the shared runtime contracts**

```bash
git add src/repo_analysis_tools/core/ids.py src/repo_analysis_tools/core/paths.py src/repo_analysis_tools/core/errors.py src/repo_analysis_tools/storage/contracts.py tests/unit/__init__.py tests/unit/test_runtime_contracts.py
git commit -m "feat: add M1 runtime and storage contracts"
```

### Task 3: Define MCP Contract Catalog and Domain Stub Tools

**Files:**
- Create: `src/repo_analysis_tools/mcp/contracts/common.py`
- Create: `src/repo_analysis_tools/mcp/contracts/__init__.py`
- Create: `src/repo_analysis_tools/mcp/contracts/scan.py`
- Create: `src/repo_analysis_tools/mcp/contracts/scope.py`
- Create: `src/repo_analysis_tools/mcp/contracts/anchors.py`
- Create: `src/repo_analysis_tools/mcp/contracts/slice.py`
- Create: `src/repo_analysis_tools/mcp/contracts/evidence.py`
- Create: `src/repo_analysis_tools/mcp/contracts/impact.py`
- Create: `src/repo_analysis_tools/mcp/contracts/report.py`
- Create: `src/repo_analysis_tools/mcp/contracts/export.py`
- Create: `src/repo_analysis_tools/mcp/app.py`
- Create: `src/repo_analysis_tools/mcp/tools/shared.py`
- Create: `src/repo_analysis_tools/mcp/tools/__init__.py`
- Create: `src/repo_analysis_tools/mcp/tools/scan_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/scope_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/anchors_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/slice_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/evidence_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/impact_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/report_tools.py`
- Create: `src/repo_analysis_tools/mcp/tools/export_tools.py`
- Create: `tests/contract/__init__.py`
- Create: `tests/contract/test_tool_contracts.py`

- [ ] **Step 1: Write the failing MCP contract tests**

```python
import unittest

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME, DOMAIN_CONTRACTS
from repo_analysis_tools.mcp.tools.shared import stub_payload


EXPECTED_DOMAINS = {
    "scan",
    "scope",
    "anchors",
    "slice",
    "evidence",
    "impact",
    "report",
    "export",
}


class ToolContractsTest(unittest.TestCase):
    def test_every_required_domain_group_exists(self) -> None:
        self.assertEqual(set(DOMAIN_CONTRACTS), EXPECTED_DOMAINS)
        for domain_name, contracts in DOMAIN_CONTRACTS.items():
            self.assertEqual(len(contracts), 3, domain_name)

    def test_every_contract_declares_shape_and_failure_modes(self) -> None:
        for contract in CONTRACT_BY_NAME.values():
            self.assertTrue(contract.input_schema, contract.name)
            self.assertTrue(contract.output_schema, contract.name)
            self.assertTrue(contract.failure_modes, contract.name)

    def test_scan_repo_stub_uses_standard_envelope(self) -> None:
        payload = stub_payload(
            "scan_repo",
            target_repo="/tmp/demo-repo",
            scan_id="scan_000000000001",
        )
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"]["scan_id"], "scan_000000000001")
        self.assertEqual(payload["recommended_next_tools"], ["get_scan_status", "show_scope"])
```

- [ ] **Step 2: Run the MCP contract tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.contract.test_tool_contracts -v`
Expected: FAIL with `ModuleNotFoundError` for `repo_analysis_tools.mcp.contracts`

- [ ] **Step 3: Write the domain contract catalog and stub tool modules**

Write `tests/contract/__init__.py`:

```python
"""Contract tests for repo-analysis-tools."""
```

Write `src/repo_analysis_tools/mcp/contracts/common.py`:

```python
from dataclasses import dataclass

from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind


@dataclass(frozen=True)
class ToolContract:
    name: str
    domain: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]
    stable_ids: tuple[StableIdKind, ...]
    failure_modes: tuple[ErrorCode, ...]
    recommended_next_tools: tuple[str, ...]
```

Write `src/repo_analysis_tools/mcp/contracts/scan.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SCAN_CONTRACTS = (
    ToolContract(
        name="scan_repo",
        domain="scan",
        input_schema={"target_repo": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.RUNTIME_STATE, ErrorCode.INTERNAL),
        recommended_next_tools=("get_scan_status", "show_scope"),
    ),
    ToolContract(
        name="refresh_scan",
        domain="scan",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "refreshed": "bool"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("get_scan_status", "show_scope"),
    ),
    ToolContract(
        name="get_scan_status",
        domain="scan",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "status_detail": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("show_scope", "list_anchors"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/scope.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SCOPE_CONTRACTS = (
    ToolContract(
        name="show_scope",
        domain="scope",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "scope_summary": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("list_scope_nodes", "list_anchors"),
    ),
    ToolContract(
        name="list_scope_nodes",
        domain="scope",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "nodes": "list"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("explain_scope_node", "list_anchors"),
    ),
    ToolContract(
        name="explain_scope_node",
        domain="scope",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "node_id": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "node_id": "string", "summary": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("list_anchors", "plan_slice"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/anchors.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


ANCHOR_CONTRACTS = (
    ToolContract(
        name="list_anchors",
        domain="anchors",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "anchors": "list"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("find_anchor", "plan_slice"),
    ),
    ToolContract(
        name="find_anchor",
        domain="anchors",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "anchor_name": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "anchor_name": "string", "matches": "list"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("describe_anchor", "plan_slice"),
    ),
    ToolContract(
        name="describe_anchor",
        domain="anchors",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "anchor_name": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "anchor_name": "string", "description": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("plan_slice", "impact_from_anchor"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/slice.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


SLICE_CONTRACTS = (
    ToolContract(
        name="plan_slice",
        domain="slice",
        input_schema={"target_repo": "string", "question": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "slice_id": "slice_<12-hex>", "seed_summary": "string"},
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("expand_slice", "build_evidence_pack"),
    ),
    ToolContract(
        name="expand_slice",
        domain="slice",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "slice_id": "slice_<12-hex>", "expanded": "bool"},
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("inspect_slice", "build_evidence_pack"),
    ),
    ToolContract(
        name="inspect_slice",
        domain="slice",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "slice_id": "slice_<12-hex>", "members": "list"},
        stable_ids=(StableIdKind.SLICE,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("build_evidence_pack", "render_focus_report"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/evidence.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


EVIDENCE_CONTRACTS = (
    ToolContract(
        name="build_evidence_pack",
        domain="evidence",
        input_schema={"target_repo": "string", "slice_id": "slice_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "slice_id": "slice_<12-hex>", "evidence_pack_id": "evidence_pack_<12-hex>"},
        stable_ids=(StableIdKind.SLICE, StableIdKind.EVIDENCE_PACK),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("read_evidence_pack", "open_span"),
    ),
    ToolContract(
        name="read_evidence_pack",
        domain="evidence",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "summary": "string"},
        stable_ids=(StableIdKind.EVIDENCE_PACK,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("open_span", "render_focus_report"),
    ),
    ToolContract(
        name="open_span",
        domain="evidence",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "path": "string", "line_start": "int", "line_end": "int"},
        output_schema={"target_repo": "string", "runtime_root": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "path": "string", "lines": "list"},
        stable_ids=(StableIdKind.EVIDENCE_PACK,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_focus_report", "summarize_impact"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/impact.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


IMPACT_CONTRACTS = (
    ToolContract(
        name="impact_from_paths",
        domain="impact",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "paths": "list"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "impact_summary": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "build_evidence_pack"),
    ),
    ToolContract(
        name="impact_from_anchor",
        domain="impact",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "anchor_name": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "impact_summary": "string"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("summarize_impact", "build_evidence_pack"),
    ),
    ToolContract(
        name="summarize_impact",
        domain="impact",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "focus": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "risks": "list"},
        stable_ids=(StableIdKind.SCAN,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_analysis_outline", "render_focus_report"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/report.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


REPORT_CONTRACTS = (
    ToolContract(
        name="render_focus_report",
        domain="report",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "report_id": "report_<12-hex>"},
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.REPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_module_summary", "export_analysis_bundle"),
    ),
    ToolContract(
        name="render_module_summary",
        domain="report",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "module_name": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "report_id": "report_<12-hex>"},
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.REPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("render_analysis_outline", "export_analysis_bundle"),
    ),
    ToolContract(
        name="render_analysis_outline",
        domain="report",
        input_schema={"target_repo": "string", "focus": "string"},
        output_schema={"target_repo": "string", "runtime_root": "string", "report_id": "report_<12-hex>", "sections": "list"},
        stable_ids=(StableIdKind.REPORT,),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_analysis_bundle", "export_scope_snapshot"),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/export.py`:

```python
from repo_analysis_tools.core.errors import ErrorCode
from repo_analysis_tools.core.ids import StableIdKind
from repo_analysis_tools.mcp.contracts.common import ToolContract


EXPORT_CONTRACTS = (
    ToolContract(
        name="export_analysis_bundle",
        domain="export",
        input_schema={"target_repo": "string", "report_id": "report_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "report_id": "report_<12-hex>", "export_id": "export_<12-hex>"},
        stable_ids=(StableIdKind.REPORT, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_scope_snapshot", "export_evidence_bundle"),
    ),
    ToolContract(
        name="export_scope_snapshot",
        domain="export",
        input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null"},
        output_schema={"target_repo": "string", "runtime_root": "string", "scan_id": "scan_<12-hex>", "export_id": "export_<12-hex>"},
        stable_ids=(StableIdKind.SCAN, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=("export_evidence_bundle",),
    ),
    ToolContract(
        name="export_evidence_bundle",
        domain="export",
        input_schema={"target_repo": "string", "evidence_pack_id": "evidence_pack_<12-hex>"},
        output_schema={"target_repo": "string", "runtime_root": "string", "evidence_pack_id": "evidence_pack_<12-hex>", "export_id": "export_<12-hex>"},
        stable_ids=(StableIdKind.EVIDENCE_PACK, StableIdKind.EXPORT),
        failure_modes=(ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.INTERNAL),
        recommended_next_tools=(),
    ),
)
```

Write `src/repo_analysis_tools/mcp/contracts/__init__.py`:

```python
from repo_analysis_tools.mcp.contracts.anchors import ANCHOR_CONTRACTS
from repo_analysis_tools.mcp.contracts.evidence import EVIDENCE_CONTRACTS
from repo_analysis_tools.mcp.contracts.export import EXPORT_CONTRACTS
from repo_analysis_tools.mcp.contracts.impact import IMPACT_CONTRACTS
from repo_analysis_tools.mcp.contracts.report import REPORT_CONTRACTS
from repo_analysis_tools.mcp.contracts.scan import SCAN_CONTRACTS
from repo_analysis_tools.mcp.contracts.scope import SCOPE_CONTRACTS
from repo_analysis_tools.mcp.contracts.slice import SLICE_CONTRACTS


DOMAIN_CONTRACTS = {
    "scan": SCAN_CONTRACTS,
    "scope": SCOPE_CONTRACTS,
    "anchors": ANCHOR_CONTRACTS,
    "slice": SLICE_CONTRACTS,
    "evidence": EVIDENCE_CONTRACTS,
    "impact": IMPACT_CONTRACTS,
    "report": REPORT_CONTRACTS,
    "export": EXPORT_CONTRACTS,
}

CONTRACT_BY_NAME = {
    contract.name: contract
    for contracts in DOMAIN_CONTRACTS.values()
    for contract in contracts
}
```

Write `src/repo_analysis_tools/mcp/app.py`:

```python
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("repo-analysis-tools", json_response=True)
```

Write `src/repo_analysis_tools/mcp/tools/shared.py`:

```python
from pathlib import Path
from typing import Any

from repo_analysis_tools.core.errors import ok_response
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME


ID_FIELDS = {
    StableIdKind.SCAN: "scan_id",
    StableIdKind.SLICE: "slice_id",
    StableIdKind.EVIDENCE_PACK: "evidence_pack_id",
    StableIdKind.REPORT: "report_id",
    StableIdKind.EXPORT: "export_id",
}


def stub_payload(tool_name: str, *, target_repo: str, **extra: Any) -> dict[str, Any]:
    contract = CONTRACT_BY_NAME[tool_name]
    payload = {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
        **extra,
    }
    for kind in contract.stable_ids:
        field_name = ID_FIELDS[kind]
        payload.setdefault(field_name, make_stable_id(kind))
    return ok_response(
        data=payload,
        messages=[f"{tool_name} is an M1 contract stub."],
        recommended_next_tools=list(contract.recommended_next_tools),
    )
```

Write `src/repo_analysis_tools/mcp/tools/scan_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def scan_repo(target_repo: str) -> dict[str, object]:
    return stub_payload("scan_repo", target_repo=target_repo)


@mcp.tool()
def refresh_scan(target_repo: str, scan_id: str) -> dict[str, object]:
    return stub_payload("refresh_scan", target_repo=target_repo, scan_id=scan_id, refreshed=True)


@mcp.tool()
def get_scan_status(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload("get_scan_status", target_repo=target_repo, scan_id=scan_id or "scan_stub_status", status_detail="stub")
```

Write `src/repo_analysis_tools/mcp/tools/scope_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def show_scope(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload("show_scope", target_repo=target_repo, scan_id=scan_id or "scan_stub_scope", scope_summary="M1 scope contract stub")


@mcp.tool()
def list_scope_nodes(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "list_scope_nodes",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_scope",
        nodes=[{"node_id": "src", "kind": "directory"}],
    )


@mcp.tool()
def explain_scope_node(target_repo: str, node_id: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "explain_scope_node",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_scope",
        node_id=node_id,
        summary="M1 scope node explanation stub",
    )
```

Write `src/repo_analysis_tools/mcp/tools/anchors_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def list_anchors(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "list_anchors",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_anchor",
        anchors=[{"name": "main", "kind": "function"}],
    )


@mcp.tool()
def find_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "find_anchor",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_anchor",
        anchor_name=anchor_name,
        matches=[{"path": "src/main.c", "line": 1}],
    )


@mcp.tool()
def describe_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "describe_anchor",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_anchor",
        anchor_name=anchor_name,
        description="M1 anchor description stub",
    )
```

Write `src/repo_analysis_tools/mcp/tools/slice_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def plan_slice(target_repo: str, question: str) -> dict[str, object]:
    return stub_payload("plan_slice", target_repo=target_repo, question=question, seed_summary="M1 slice planning stub")


@mcp.tool()
def expand_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload("expand_slice", target_repo=target_repo, slice_id=slice_id, expanded=True)


@mcp.tool()
def inspect_slice(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload(
        "inspect_slice",
        target_repo=target_repo,
        slice_id=slice_id,
        members=[{"path": "src/main.c", "reason": "seed"}],
    )
```

Write `src/repo_analysis_tools/mcp/tools/evidence_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def build_evidence_pack(target_repo: str, slice_id: str) -> dict[str, object]:
    return stub_payload("build_evidence_pack", target_repo=target_repo, slice_id=slice_id)


@mcp.tool()
def read_evidence_pack(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload(
        "read_evidence_pack",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        summary="M1 evidence pack stub",
    )


@mcp.tool()
def open_span(target_repo: str, evidence_pack_id: str, path: str, line_start: int, line_end: int) -> dict[str, object]:
    return stub_payload(
        "open_span",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        path=path,
        line_start=line_start,
        line_end=line_end,
        lines=["/* M1 span stub */"],
    )
```

Write `src/repo_analysis_tools/mcp/tools/impact_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def impact_from_paths(target_repo: str, paths: list[str], scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "impact_from_paths",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_impact",
        paths=paths,
        impact_summary="M1 path impact stub",
    )


@mcp.tool()
def impact_from_anchor(target_repo: str, anchor_name: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "impact_from_anchor",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_impact",
        anchor_name=anchor_name,
        impact_summary="M1 anchor impact stub",
    )


@mcp.tool()
def summarize_impact(target_repo: str, focus: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload(
        "summarize_impact",
        target_repo=target_repo,
        scan_id=scan_id or "scan_stub_impact",
        focus=focus,
        risks=["M1 stub risk"],
    )
```

Write `src/repo_analysis_tools/mcp/tools/report_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def render_focus_report(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload("render_focus_report", target_repo=target_repo, evidence_pack_id=evidence_pack_id)


@mcp.tool()
def render_module_summary(target_repo: str, evidence_pack_id: str, module_name: str) -> dict[str, object]:
    return stub_payload(
        "render_module_summary",
        target_repo=target_repo,
        evidence_pack_id=evidence_pack_id,
        module_name=module_name,
    )


@mcp.tool()
def render_analysis_outline(target_repo: str, focus: str) -> dict[str, object]:
    return stub_payload(
        "render_analysis_outline",
        target_repo=target_repo,
        focus=focus,
        sections=["summary", "evidence", "risks"],
    )
```

Write `src/repo_analysis_tools/mcp/tools/export_tools.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.tools.shared import stub_payload


@mcp.tool()
def export_analysis_bundle(target_repo: str, report_id: str) -> dict[str, object]:
    return stub_payload("export_analysis_bundle", target_repo=target_repo, report_id=report_id)


@mcp.tool()
def export_scope_snapshot(target_repo: str, scan_id: str | None = None) -> dict[str, object]:
    return stub_payload("export_scope_snapshot", target_repo=target_repo, scan_id=scan_id or "scan_stub_export")


@mcp.tool()
def export_evidence_bundle(target_repo: str, evidence_pack_id: str) -> dict[str, object]:
    return stub_payload("export_evidence_bundle", target_repo=target_repo, evidence_pack_id=evidence_pack_id)
```

Write `src/repo_analysis_tools/mcp/tools/__init__.py`:

```python
from . import anchors_tools, evidence_tools, export_tools, impact_tools, report_tools, scan_tools, scope_tools, slice_tools

__all__ = [
    "anchors_tools",
    "evidence_tools",
    "export_tools",
    "impact_tools",
    "report_tools",
    "scan_tools",
    "scope_tools",
    "slice_tools",
]
```

- [ ] **Step 4: Run the MCP contract tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.contract.test_tool_contracts -v`
Expected: PASS with tests for domain coverage, shape coverage, and standard response envelopes

- [ ] **Step 5: Commit the MCP contract catalog**

```bash
git add src/repo_analysis_tools/mcp/app.py src/repo_analysis_tools/mcp/contracts src/repo_analysis_tools/mcp/tools tests/contract/__init__.py tests/contract/test_tool_contracts.py
git commit -m "feat: add M1 MCP contract stubs"
```

### Task 4: Boot the FastMCP Server

**Files:**
- Modify: `pyproject.toml`
- Create: `src/repo_analysis_tools/mcp/server.py`
- Create: `tests/smoke/test_mcp_server.py`

- [ ] **Step 1: Write the failing MCP server smoke test**

```python
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest


class McpServerSmokeTest(unittest.TestCase):
    def test_server_process_starts_under_stdio(self) -> None:
        src_root = Path(__file__).resolve().parents[2] / "src"
        env = dict(os.environ)
        env["PYTHONPATH"] = str(src_root)
        process = subprocess.Popen(
            [sys.executable, "-m", "repo_analysis_tools.mcp.server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        try:
            time.sleep(1)
            poll_result = process.poll()
            if poll_result is not None:
                stderr_output = process.stderr.read()
                self.fail(f"server exited early: {stderr_output}")
        finally:
            process.terminate()
            process.wait(timeout=5)
```

- [ ] **Step 2: Run the smoke test and verify it fails**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.smoke.test_mcp_server -v`
Expected: FAIL with `No module named repo_analysis_tools.mcp.server`

- [ ] **Step 3: Write the stdio MCP server entrypoint and console script**

Update `pyproject.toml`:

```toml
[project.scripts]
repo-analysis-mcp = "repo_analysis_tools.mcp.server:main"
```

Write `src/repo_analysis_tools/mcp/server.py`:

```python
from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp import tools as registered_tools


def create_server():
    return mcp


def main() -> None:
    _ = registered_tools
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the server smoke test and verify it passes**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.smoke.test_mcp_server -v`
Expected: PASS with the child process alive after one second and then terminating cleanly

- [ ] **Step 5: Commit the server bootstrap**

```bash
git add pyproject.toml src/repo_analysis_tools/mcp/server.py tests/smoke/test_mcp_server.py
git commit -m "feat: add M1 FastMCP server bootstrap"
```

### Task 5: Add Contract Golden Harness

**Files:**
- Create: `tests/golden/__init__.py`
- Create: `tests/golden/harness.py`
- Create: `tests/golden/fixtures/scan_repo.json`
- Create: `tests/golden/test_contract_golden.py`

- [ ] **Step 1: Write the failing golden test**

```python
import unittest

from repo_analysis_tools.mcp.tools.shared import stub_payload
from tests.golden.harness import assert_matches_golden


class ContractGoldenTest(unittest.TestCase):
    def test_scan_repo_stub_matches_golden_fixture(self) -> None:
        payload = stub_payload(
            "scan_repo",
            target_repo="/tmp/demo-repo",
            scan_id="scan_000000000001",
        )
        assert_matches_golden(self, "scan_repo.json", payload)
```

- [ ] **Step 2: Run the golden test and verify it fails**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.golden.test_contract_golden -v`
Expected: FAIL with `ModuleNotFoundError` for `tests.golden.harness`

- [ ] **Step 3: Write the golden harness and fixture**

Write `tests/golden/__init__.py`:

```python
"""Golden tests for repo-analysis-tools."""
```

Write `tests/golden/harness.py`:

```python
import json
from pathlib import Path


GOLDEN_ROOT = Path(__file__).resolve().parent / "fixtures"


def load_golden(name: str) -> dict[str, object]:
    return json.loads((GOLDEN_ROOT / name).read_text(encoding="utf-8"))


def assert_matches_golden(testcase, name: str, payload: dict[str, object]) -> None:
    testcase.assertEqual(payload, load_golden(name))
```

Write `tests/golden/fixtures/scan_repo.json`:

```json
{
  "schema_version": "1",
  "status": "ok",
  "data": {
    "target_repo": "/tmp/demo-repo",
    "runtime_root": "/tmp/demo-repo/.codewiki",
    "scan_id": "scan_000000000001"
  },
  "messages": [
    {
      "level": "info",
      "text": "scan_repo is an M1 contract stub."
    }
  ],
  "recommended_next_tools": [
    "get_scan_status",
    "show_scope"
  ]
}
```

Write `tests/golden/test_contract_golden.py`:

```python
import unittest

from repo_analysis_tools.mcp.tools.shared import stub_payload
from tests.golden.harness import assert_matches_golden


class ContractGoldenTest(unittest.TestCase):
    def test_scan_repo_stub_matches_golden_fixture(self) -> None:
        payload = stub_payload(
            "scan_repo",
            target_repo="/tmp/demo-repo",
            scan_id="scan_000000000001",
        )
        assert_matches_golden(self, "scan_repo.json", payload)
```

- [ ] **Step 4: Run the contract and golden tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.contract.test_tool_contracts tests.golden.test_contract_golden -v`
Expected: PASS with both contract validation and the starter golden snapshot succeeding

- [ ] **Step 5: Commit the golden harness**

```bash
git add tests/golden/__init__.py tests/golden/harness.py tests/golden/fixtures/scan_repo.json tests/golden/test_contract_golden.py
git commit -m "feat: add M1 contract golden harness"
```

### Task 6: Publish Architecture and Contract Documentation

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/contracts/mcp-tool-contracts.md`
- Create: `tests/unit/test_architecture_docs.py`

- [ ] **Step 1: Write the failing documentation tests**

```python
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.contracts import CONTRACT_BY_NAME


ROOT = Path(__file__).resolve().parents[2]


class ArchitectureDocsTest(unittest.TestCase):
    def test_architecture_doc_mentions_runtime_root_and_storage_owners(self) -> None:
        text = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
        self.assertIn(".codewiki/", text)
        for domain_name in ("scan", "scope", "anchors", "slice", "evidence", "impact", "report", "export"):
            self.assertIn(f"`{domain_name}`", text)

    def test_contract_doc_lists_every_tool(self) -> None:
        text = (ROOT / "docs" / "contracts" / "mcp-tool-contracts.md").read_text(encoding="utf-8")
        for tool_name in CONTRACT_BY_NAME:
            self.assertIn(f"`{tool_name}`", text)
```

- [ ] **Step 2: Run the documentation tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_architecture_docs -v`
Expected: FAIL with `FileNotFoundError` for `docs/architecture.md`

- [ ] **Step 3: Write the architecture-facing documents**

Write `docs/architecture.md`:

```md
# Repository Architecture

## Purpose

M1 freezes the top-level repository skeleton and MCP contracts for the new repository analysis platform.

## Package Boundaries

The repository keeps explicit top-level boundaries for:

- `core`
- `storage`
- `scan`
- `scope`
- `anchors`
- `slice`
- `evidence`
- `impact`
- `report`
- `export`
- `mcp`
- `skills`
- `doc_specs`
- `doc_dsl`
- `renderers`
- `tests`

## Runtime Root

All per-target runtime state lives under `<target_repo>/.codewiki/`.

No client-specific runtime directory such as `.claude/` is allowed back into the platform.

## Storage Ownership

| Domain | Runtime directory | Owned artifacts |
| --- | --- | --- |
| `scan` | `.codewiki/scan/` | scan metadata and scan handles |
| `scope` | `.codewiki/scope/` | scope snapshots derived from scans |
| `anchors` | `.codewiki/anchors/` | extracted anchor facts |
| `slice` | `.codewiki/slice/` | slice manifests and expansions |
| `evidence` | `.codewiki/evidence/` | evidence packs and citations |
| `impact` | `.codewiki/impact/` | impact analysis artifacts |
| `report` | `.codewiki/report/` | structured report payloads |
| `export` | `.codewiki/export/` | exported bundles and snapshots |

## Shared Contracts

- Stable IDs exist for scans, slices, evidence packs, reports, and exports.
- Every MCP tool returns the same top-level response envelope: `schema_version`, `status`, `data`, `messages`, and `recommended_next_tools`.
- Every MCP-facing failure is classified through the shared error taxonomy in `repo_analysis_tools.core.errors`.

## M1 Exit Condition

After M1, later milestones can add real domain behavior without renaming top-level packages, moving runtime directories, or changing the response envelope.
```

Write `docs/contracts/mcp-tool-contracts.md`:

````md
# MCP Tool Contracts

## Common Envelope

Every MCP tool returns:

```json
{
  "schema_version": "1",
  "status": "ok|error",
  "data": {},
  "messages": [],
  "recommended_next_tools": []
}
```

## Scan

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `scan_repo` | `target_repo` | `target_repo`, `runtime_root`, `scan_id` | `invalid_input`, `runtime_state`, `internal` |
| `refresh_scan` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `refreshed` | `invalid_input`, `not_found`, `internal` |
| `get_scan_status` | `target_repo`, `scan_id?` | `target_repo`, `runtime_root`, `scan_id`, `status_detail` | `invalid_input`, `not_found`, `internal` |

## Scope

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `show_scope` | `target_repo`, `scan_id?` | `target_repo`, `runtime_root`, `scan_id`, `scope_summary` | `invalid_input`, `not_found`, `internal` |
| `list_scope_nodes` | `target_repo`, `scan_id?` | `target_repo`, `runtime_root`, `scan_id`, `nodes` | `invalid_input`, `not_found`, `internal` |
| `explain_scope_node` | `target_repo`, `scan_id?`, `node_id` | `target_repo`, `runtime_root`, `scan_id`, `node_id`, `summary` | `invalid_input`, `not_found`, `internal` |

## Anchors

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `list_anchors` | `target_repo`, `scan_id?` | `target_repo`, `runtime_root`, `scan_id`, `anchors` | `invalid_input`, `not_found`, `internal` |
| `find_anchor` | `target_repo`, `scan_id?`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `matches` | `invalid_input`, `not_found`, `internal` |
| `describe_anchor` | `target_repo`, `scan_id?`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `description` | `invalid_input`, `not_found`, `internal` |

## Slice

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `plan_slice` | `target_repo`, `question` | `target_repo`, `runtime_root`, `slice_id`, `seed_summary` | `invalid_input`, `not_found`, `internal` |
| `expand_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `expanded` | `invalid_input`, `not_found`, `internal` |
| `inspect_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `members` | `invalid_input`, `not_found`, `internal` |

## Evidence

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `build_evidence_pack` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `evidence_pack_id` | `invalid_input`, `not_found`, `internal` |
| `read_evidence_pack` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `summary` | `invalid_input`, `not_found`, `internal` |
| `open_span` | `target_repo`, `evidence_pack_id`, `path`, `line_start`, `line_end` | `target_repo`, `runtime_root`, `evidence_pack_id`, `path`, `lines` | `invalid_input`, `not_found`, `internal` |

## Impact

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `impact_from_paths` | `target_repo`, `scan_id?`, `paths` | `target_repo`, `runtime_root`, `scan_id`, `impact_summary` | `invalid_input`, `not_found`, `internal` |
| `impact_from_anchor` | `target_repo`, `scan_id?`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `impact_summary` | `invalid_input`, `not_found`, `internal` |
| `summarize_impact` | `target_repo`, `scan_id?`, `focus` | `target_repo`, `runtime_root`, `scan_id`, `risks` | `invalid_input`, `not_found`, `internal` |

## Report

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `render_focus_report` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `report_id` | `invalid_input`, `not_found`, `internal` |
| `render_module_summary` | `target_repo`, `evidence_pack_id`, `module_name` | `target_repo`, `runtime_root`, `evidence_pack_id`, `report_id` | `invalid_input`, `not_found`, `internal` |
| `render_analysis_outline` | `target_repo`, `focus` | `target_repo`, `runtime_root`, `report_id`, `sections` | `invalid_input`, `not_found`, `internal` |

## Export

| Tool | Input shape | Output shape | Failure modes |
| --- | --- | --- | --- |
| `export_analysis_bundle` | `target_repo`, `report_id` | `target_repo`, `runtime_root`, `report_id`, `export_id` | `invalid_input`, `not_found`, `internal` |
| `export_scope_snapshot` | `target_repo`, `scan_id?` | `target_repo`, `runtime_root`, `scan_id`, `export_id` | `invalid_input`, `not_found`, `internal` |
| `export_evidence_bundle` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `export_id` | `invalid_input`, `not_found`, `internal` |
````

- [ ] **Step 4: Run the full test suite and verify it passes**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest discover -s tests -t . -v`
Expected: PASS with smoke, unit, contract, and golden tests all succeeding

- [ ] **Step 5: Commit the M1 documentation baseline**

```bash
git add docs/architecture.md docs/contracts/mcp-tool-contracts.md tests/unit/test_architecture_docs.py
git commit -m "docs: add M1 architecture and MCP contract docs"
```
