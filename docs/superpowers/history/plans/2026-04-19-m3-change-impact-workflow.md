# M3 Change-Impact Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `refresh_scan -> impact_from_paths / impact_from_anchor -> summarize_impact -> inspect related anchors or slices -> build_evidence_pack` usable for real C repository change analysis with explicit uncertainty and regression guidance.

**Architecture:** Build M3 around persisted impact artifacts under `<target_repo>/.codewiki/impact/` so `impact_from_paths` and `impact_from_anchor` produce reusable structured results instead of prose-only summaries. Introduce an `impact_id` handle so `summarize_impact` can operate on recorded impact facts rather than recomputing from vague `focus` strings. Keep the `change-impact` skill orchestration-only: the MCP tools own propagation logic, risk shaping, and evidence boundaries.

**Tech Stack:** Python 3.11 (`/home/hyx/anaconda3/envs/agent/bin/python`), stdlib `unittest`, stdlib `json`, existing scan/scope/anchors/slice/evidence services, MCP Python SDK (`mcp[cli]`), Markdown skill files under `.agents/skills/`

---

## File Structure

- Modify: `src/repo_analysis_tools/core/ids.py`
  Responsibility: add deterministic `impact_<12-hex>` stable IDs for persisted impact artifacts.
- Create: `src/repo_analysis_tools/impact/models.py`
  Responsibility: define typed impact records, propagation targets, and risk findings.
- Create: `src/repo_analysis_tools/impact/store.py`
  Responsibility: persist and reload impact artifacts under `.codewiki/impact/`.
- Create: `src/repo_analysis_tools/impact/propagation.py`
  Responsibility: compute direct impact and likely propagation from anchors, reverse call edges, and include-style relations when present.
- Create: `src/repo_analysis_tools/impact/service.py`
  Responsibility: resolve path and anchor seeds, build impact artifacts, and derive structured risk summaries.
- Modify: `src/repo_analysis_tools/mcp/contracts/impact.py`
  Responsibility: replace M1 stub schemas with real M3 impact payloads.
- Modify: `src/repo_analysis_tools/mcp/tools/impact_tools.py`
  Responsibility: replace M1 stubs with service-backed implementations.
- Create: `tests/unit/test_impact_service.py`
  Responsibility: validate impact artifact persistence, propagation rules, uncertainty notes, and regression focus selection.
- Modify: `tests/contract/test_tool_contracts.py`
  Responsibility: verify the real impact tool signatures, payloads, and recommended-next-tool flow.
- Modify: `tests/golden/test_contract_golden.py`
  Responsibility: snapshot a deterministic `summarize_impact` payload backed by real services.
- Create: `tests/golden/fixtures/summarize_impact_scope_first.json`
  Responsibility: golden fixture for the first deterministic impact summary.
- Create: `tests/integration/test_change_impact_workflow.py`
  Responsibility: prove the synthetic repository supports the M3 change-impact path end to end.
- Create: `tests/e2e/test_change_impact_easyflash.py`
  Responsibility: validate one realistic change scenario against the checked-in EasyFlash fixture.
- Create: `.agents/skills/change-impact/SKILL.md`
  Responsibility: Codex workflow skill for evidence-backed change impact analysis.
- Modify: `docs/architecture.md`
  Responsibility: document the M3 change-impact handoff and persisted impact artifacts.
- Modify: `docs/contracts/mcp-tool-contracts.md`
  Responsibility: document the real M3 impact contracts.

## Working Set

- Parent design: `docs/superpowers/specs/2026-04-17-repo-analysis-platform-design.md`
- M3 spec: `docs/superpowers/specs/2026-04-17-m3-change-impact-workflow-spec.md`
- Existing M2 plan: `docs/superpowers/plans/2026-04-19-m2-analysis-first-mainline.md`
- Existing synthetic fixture: `tests/fixtures/scope_first_repo.py`
- Existing real fixture helper: `tests/fixtures/easyflash_repo.py`
- Existing anchor relation runtime: `src/repo_analysis_tools/anchors/`
- Existing evidence workflow: `src/repo_analysis_tools/evidence/`

## Design Assumption

This plan introduces a persisted `impact_id` artifact even though M2 only formalized stable handles for scan, slice, evidence, report, and export. That is an intentional M3 expansion to keep impact analysis structured, reusable, and non-duplicative across `impact_from_*`, `summarize_impact`, and the `change-impact` skill.

### Task 1: Implement the Impact Core with Persisted Artifacts

**Files:**
- Modify: `src/repo_analysis_tools/core/ids.py`
- Create: `src/repo_analysis_tools/impact/models.py`
- Create: `src/repo_analysis_tools/impact/store.py`
- Create: `src/repo_analysis_tools/impact/propagation.py`
- Create: `src/repo_analysis_tools/impact/service.py`
- Create: `tests/unit/test_impact_service.py`

- [ ] **Step 1: Write the failing unit tests**

Create `tests/unit/test_impact_service.py`:

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.impact.service import ImpactService
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ImpactServiceTest(unittest.TestCase):
    def test_from_paths_persists_changed_path_and_reverse_callers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan = ScanService().scan(repo)

            impact = ImpactService().from_paths(repo, ["src/flash.c"], scan_id=scan.scan_id)

            self.assertRegex(impact.impact_id, r"^impact_[0-9a-f]{12}$")
            self.assertEqual(impact.scan_id, scan.scan_id)
            self.assertEqual(impact.changed_paths, ["src/flash.c"])
            self.assertEqual([item.path for item in impact.direct_impacts], ["src/flash.c"])
            self.assertEqual(
                {item.path for item in impact.likely_propagation},
                {"demo/demo_main.c", "src/main.c"},
            )
            self.assertIn("anchor relations", impact.uncertainty_notes[0])

    def test_from_anchor_uses_anchor_seed_and_caller_propagation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan = ScanService().scan(repo)

            impact = ImpactService().from_anchor(repo, "flash_init", scan_id=scan.scan_id)

            self.assertEqual(impact.seed_kind, "anchor")
            self.assertEqual(impact.seed_value, "flash_init")
            self.assertEqual({item.anchor_name for item in impact.likely_propagation}, {"demo_main", "main"})

    def test_summarize_returns_structured_risks_and_regression_focus(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan = ScanService().scan(repo)
            impact = ImpactService().from_paths(repo, ["src/flash.c"], scan_id=scan.scan_id)

            summary = ImpactService().summarize(repo, impact.impact_id)

            self.assertEqual(summary.impact_id, impact.impact_id)
            self.assertTrue(summary.confirmed_impact)
            self.assertTrue(summary.likely_propagation)
            self.assertTrue(summary.regression_focus)
            self.assertTrue(summary.blind_spots)
            self.assertTrue(summary.risks)
```

- [ ] **Step 2: Run the unit tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_impact_service -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'repo_analysis_tools.impact.service'`.

- [ ] **Step 3: Add the stable ID and typed impact models**

Update `src/repo_analysis_tools/core/ids.py`:

```python
class StableIdKind(StrEnum):
    SCAN = "scan"
    SLICE = "slice"
    EVIDENCE_PACK = "evidence_pack"
    IMPACT = "impact"
    REPORT = "report"
    EXPORT = "export"
```

Write `src/repo_analysis_tools/impact/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImpactTarget:
    path: str
    anchor_name: str | None
    reason: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "anchor_name": self.anchor_name,
            "reason": self.reason,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class RiskFinding:
    level: str
    title: str
    summary: str
    supporting_paths: list[str]
    supporting_anchor_names: list[str]
    uncertainty: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "title": self.title,
            "summary": self.summary,
            "supporting_paths": self.supporting_paths,
            "supporting_anchor_names": self.supporting_anchor_names,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class ImpactRecord:
    impact_id: str
    scan_id: str
    seed_kind: str
    seed_value: str
    changed_paths: list[str]
    direct_impacts: list[ImpactTarget]
    likely_propagation: list[ImpactTarget]
    uncertainty_notes: list[str]
    regression_focus: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "impact_id": self.impact_id,
            "scan_id": self.scan_id,
            "seed_kind": self.seed_kind,
            "seed_value": self.seed_value,
            "changed_paths": self.changed_paths,
            "direct_impacts": [item.to_dict() for item in self.direct_impacts],
            "likely_propagation": [item.to_dict() for item in self.likely_propagation],
            "uncertainty_notes": self.uncertainty_notes,
            "regression_focus": self.regression_focus,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ImpactSummary:
    impact_id: str
    scan_id: str
    confirmed_impact: list[ImpactTarget]
    likely_propagation: list[ImpactTarget]
    regression_focus: list[str]
    blind_spots: list[str]
    risks: list[RiskFinding]
    summary: str
```

- [ ] **Step 4: Add persistence and propagation helpers**

Write `src/repo_analysis_tools/impact/store.py`:

```python
from __future__ import annotations

from repo_analysis_tools.impact.models import ImpactRecord
from repo_analysis_tools.storage.json_assets import JsonAssetStore


class ImpactStore:
    def __init__(self, target_repo: str) -> None:
        self.assets = JsonAssetStore(target_repo, "impact")

    @classmethod
    def for_repo(cls, target_repo: str) -> "ImpactStore":
        return cls(target_repo)

    def save(self, record: ImpactRecord) -> None:
        self.assets.write_json(f"results/{record.impact_id}.json", record.to_dict())
        self.assets.write_json("latest.json", {"impact_id": record.impact_id})
```

Write `src/repo_analysis_tools/impact/propagation.py`:

```python
from __future__ import annotations

from repo_analysis_tools.anchors.models import AnchorRecord, AnchorRelation
from repo_analysis_tools.impact.models import ImpactTarget


def reverse_callers(seed_anchors: list[AnchorRecord], anchors: list[AnchorRecord], relations: list[AnchorRelation]) -> list[ImpactTarget]:
    anchor_by_id = {anchor.anchor_id: anchor for anchor in anchors}
    seed_ids = {anchor.anchor_id for anchor in seed_anchors}
    targets: dict[tuple[str, str | None], ImpactTarget] = {}

    for relation in relations:
        if relation.target_anchor_id not in seed_ids:
            continue
        caller = anchor_by_id.get(relation.source_anchor_id)
        if caller is None:
            continue
        key = (caller.path, caller.name)
        targets[key] = ImpactTarget(
            path=caller.path,
            anchor_name=caller.name,
            reason=f"{caller.name} {relation.kind} {relation.target_name}",
            confidence="likely",
        )

    return sorted(targets.values(), key=lambda item: (item.path, item.anchor_name or ""))
```

- [ ] **Step 5: Implement the orchestration service**

Write the core of `src/repo_analysis_tools/impact/service.py`:

```python
from __future__ import annotations

from pathlib import Path

from repo_analysis_tools.anchors.store import AnchorStore
from repo_analysis_tools.core.ids import StableIdKind, make_stable_id
from repo_analysis_tools.core.paths import normalize_repo_relative_path
from repo_analysis_tools.impact.models import ImpactRecord, ImpactSummary, ImpactTarget, RiskFinding
from repo_analysis_tools.impact.propagation import reverse_callers
from repo_analysis_tools.impact.store import ImpactStore
from repo_analysis_tools.scan.store import ScanStore


class ImpactService:
    def from_paths(self, target_repo: Path | str, paths: list[str], scan_id: str | None = None) -> ImpactRecord:
        repo = Path(target_repo).expanduser().resolve()
        scan = ScanStore.for_repo(repo).load(scan_id=scan_id)
        anchors = AnchorStore.for_repo(repo).load(scan.scan_id)
        changed_paths = sorted({normalize_repo_relative_path(repo, path) for path in paths})
        seed_anchors = [anchor for anchor in anchors.anchors if anchor.path in changed_paths]
        propagation = reverse_callers(seed_anchors, anchors.anchors, anchors.relations)
        record = ImpactRecord(
            impact_id=make_stable_id(StableIdKind.IMPACT),
            scan_id=scan.scan_id,
            seed_kind="paths",
            seed_value=",".join(changed_paths),
            changed_paths=changed_paths,
            direct_impacts=[
                ImpactTarget(path=path, anchor_name=None, reason="changed path", confidence="confirmed")
                for path in changed_paths
            ],
            likely_propagation=propagation,
            uncertainty_notes=[
                "Propagation is limited to extracted anchor relations and does not model runtime-only behavior."
            ],
            regression_focus=sorted({item.anchor_name for item in propagation if item.anchor_name}),
            summary=f"{len(changed_paths)} changed path(s), {len(propagation)} likely propagation target(s).",
        )
        ImpactStore.for_repo(repo).save(record)
        return record

    def from_anchor(self, target_repo: Path | str, anchor_name: str, scan_id: str | None = None) -> ImpactRecord:
        repo = Path(target_repo).expanduser().resolve()
        scan = ScanStore.for_repo(repo).load(scan_id=scan_id)
        anchors = AnchorStore.for_repo(repo).load(scan.scan_id)
        seed_anchors = [anchor for anchor in anchors.anchors if anchor.name == anchor_name]
        if not seed_anchors:
            raise FileNotFoundError(f"anchor {anchor_name} was not found")
        return self.from_paths(repo, [seed_anchors[0].path], scan_id=scan.scan_id)

    def summarize(self, target_repo: Path | str, impact_id: str) -> ImpactSummary:
        repo = Path(target_repo).expanduser().resolve()
        record = ImpactStore.for_repo(repo).load(impact_id)
        return ImpactSummary(
            impact_id=record.impact_id,
            scan_id=record.scan_id,
            confirmed_impact=record.direct_impacts,
            likely_propagation=record.likely_propagation,
            regression_focus=record.regression_focus,
            blind_spots=list(record.uncertainty_notes),
            risks=[
                RiskFinding(
                    level="medium",
                    title="Callers may need regression coverage",
                    summary=record.summary,
                    supporting_paths=[item.path for item in record.likely_propagation],
                    supporting_anchor_names=[item.anchor_name for item in record.likely_propagation if item.anchor_name],
                    uncertainty=record.uncertainty_notes[0] if record.uncertainty_notes else None,
                )
            ],
            summary=record.summary,
        )
```

- [ ] **Step 6: Run the unit tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_impact_service -v`
Expected: PASS with all `ImpactServiceTest` cases green.

- [ ] **Step 7: Commit the impact core**

```bash
git add src/repo_analysis_tools/core/ids.py src/repo_analysis_tools/impact tests/unit/test_impact_service.py
git commit -m "feat: implement impact analysis core"
```

### Task 2: Wire the Real Impact MCP Tools and Contracts

**Files:**
- Modify: `src/repo_analysis_tools/mcp/contracts/impact.py`
- Modify: `src/repo_analysis_tools/mcp/tools/impact_tools.py`
- Modify: `tests/contract/test_tool_contracts.py`
- Modify: `docs/contracts/mcp-tool-contracts.md`

- [ ] **Step 1: Write the failing contract assertions**

Update `tests/contract/test_tool_contracts.py`:

```python
TOOL_CALL_KWARGS.update(
    {
        "impact_from_paths": {"target_repo": "/tmp/demo-repo", "paths": ["src/flash.c"]},
        "impact_from_anchor": {"target_repo": "/tmp/demo-repo", "anchor_name": "flash_init"},
        "summarize_impact": {"target_repo": "/tmp/demo-repo", "impact_id": "impact_000000000001"},
    }
)
```

Add these tests:

```python
def test_impact_tools_use_real_services(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = build_scope_first_repo(Path(tmpdir))
        scan_payload = scan_repo(str(repo))

        paths_payload = impact_tools.impact_from_paths(str(repo), ["src/flash.c"], scan_payload["data"]["scan_id"])
        anchor_payload = impact_tools.impact_from_anchor(str(repo), "flash_init", scan_payload["data"]["scan_id"])
        summary_payload = impact_tools.summarize_impact(str(repo), paths_payload["data"]["impact_id"])

        self.assertEqual(paths_payload["status"], "ok")
        self.assertRegex(paths_payload["data"]["impact_id"], r"^impact_[0-9a-f]{12}$")
        self.assertEqual(paths_payload["data"]["changed_paths"], ["src/flash.c"])
        self.assertEqual(
            {item["path"] for item in paths_payload["data"]["likely_propagation"]},
            {"demo/demo_main.c", "src/main.c"},
        )
        self.assertEqual(anchor_payload["data"]["seed_kind"], "anchor")
        self.assertTrue(summary_payload["data"]["risks"])
        self.assertEqual(summary_payload["recommended_next_tools"], ["plan_slice", "build_evidence_pack"])
```

- [ ] **Step 2: Run the contract tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.contract.test_tool_contracts -v`
Expected: FAIL because the impact contract schemas still declare M1 stub fields and `summarize_impact` still accepts `focus` instead of `impact_id`.

- [ ] **Step 3: Replace the M1 impact contracts**

Update `src/repo_analysis_tools/mcp/contracts/impact.py`:

```python
ToolContract(
    name="impact_from_paths",
    domain="impact",
    input_schema={"target_repo": "string", "scan_id": "scan_<12-hex>|null", "paths": "list"},
    output_schema={
        "target_repo": "string",
        "runtime_root": "string",
        "scan_id": "scan_<12-hex>",
        "impact_id": "impact_<12-hex>",
        "seed_kind": "string",
        "changed_paths": "list",
        "direct_impacts": "list",
        "likely_propagation": "list",
        "uncertainty_notes": "list",
        "recommended_regression_focus": "list",
        "summary": "string",
    },
    stable_ids=(StableIdKind.SCAN, StableIdKind.IMPACT),
    recommended_next_tools=("summarize_impact", "plan_slice"),
)
```

Mirror the same structure for `impact_from_anchor`, replacing `changed_paths` with `anchor_name`.

Define `summarize_impact` as:

```python
ToolContract(
    name="summarize_impact",
    domain="impact",
    input_schema={"target_repo": "string", "impact_id": "impact_<12-hex>"},
    output_schema={
        "target_repo": "string",
        "runtime_root": "string",
        "impact_id": "impact_<12-hex>",
        "scan_id": "scan_<12-hex>",
        "confirmed_impact": "list",
        "likely_propagation": "list",
        "regression_focus": "list",
        "blind_spots": "list",
        "risks": "list",
        "summary": "string",
    },
    stable_ids=(StableIdKind.IMPACT,),
    recommended_next_tools=("plan_slice", "build_evidence_pack"),
)
```

- [ ] **Step 4: Wire the service-backed impact tools**

Write `src/repo_analysis_tools/mcp/tools/impact_tools.py`:

```python
from pathlib import Path

from repo_analysis_tools.core.errors import ErrorCode, error_response, ok_response
from repo_analysis_tools.core.paths import runtime_root
from repo_analysis_tools.impact.service import ImpactService
from repo_analysis_tools.mcp.app import mcp


def _impact_base_payload(target_repo: str, scan_id: str | None = None, impact_id: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "target_repo": target_repo,
        "runtime_root": runtime_root(Path(target_repo)).as_posix(),
    }
    if scan_id is not None:
        payload["scan_id"] = scan_id
    if impact_id is not None:
        payload["impact_id"] = impact_id
    return payload


@mcp.tool()
def impact_from_paths(target_repo: str, paths: list[str], scan_id: str | None = None) -> dict[str, object]:
    try:
        impact = ImpactService().from_paths(target_repo, paths, scan_id=scan_id)
    except ValueError as exc:
        return error_response(ErrorCode.INVALID_INPUT, str(exc))
    except FileNotFoundError as exc:
        return error_response(ErrorCode.NOT_FOUND, str(exc))
    return ok_response(
        data={
            **_impact_base_payload(target_repo, scan_id=impact.scan_id, impact_id=impact.impact_id),
            "seed_kind": impact.seed_kind,
            "changed_paths": impact.changed_paths,
            "direct_impacts": [item.to_dict() for item in impact.direct_impacts],
            "likely_propagation": [item.to_dict() for item in impact.likely_propagation],
            "uncertainty_notes": impact.uncertainty_notes,
            "recommended_regression_focus": impact.regression_focus,
            "summary": impact.summary,
        },
        messages=["impact artifact built from changed paths"],
        recommended_next_tools=["summarize_impact", "plan_slice"],
    )
```

Implement `impact_from_anchor` and `summarize_impact` the same way, with `impact_id`-backed loading for summary.

- [ ] **Step 5: Sync the contract documentation rows**

Update the `impact` table in `docs/contracts/mcp-tool-contracts.md` so the rows match the new schemas exactly.

- [ ] **Step 6: Run the contract tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.contract.test_tool_contracts tests.unit.test_architecture_docs -v`
Expected: PASS with real impact tool payloads and contract docs aligned.

- [ ] **Step 7: Commit the real impact MCP surface**

```bash
git add src/repo_analysis_tools/mcp/contracts/impact.py src/repo_analysis_tools/mcp/tools/impact_tools.py tests/contract/test_tool_contracts.py docs/contracts/mcp-tool-contracts.md
git commit -m "feat: wire real impact MCP tools"
```

### Task 3: Add Golden Coverage and the Synthetic Change-Impact Workflow

**Files:**
- Modify: `tests/golden/test_contract_golden.py`
- Create: `tests/golden/fixtures/summarize_impact_scope_first.json`
- Create: `tests/integration/test_change_impact_workflow.py`

- [ ] **Step 1: Write the failing golden and integration tests**

Create `tests/integration/test_change_impact_workflow.py`:

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.scan_tools import refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.scope_first_repo import build_scope_first_repo


class ChangeImpactWorkflowTest(unittest.TestCase):
    def test_scope_first_repo_change_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            created = scan_repo(str(repo))
            refreshed = refresh_scan(str(repo), created["data"]["scan_id"])
            impact_payload = impact_from_paths(str(repo), ["src/flash.c"], refreshed["data"]["scan_id"])
            summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
            slice_payload = plan_slice(str(repo), "Where is flash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), slice_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), evidence_payload["data"]["evidence_pack_id"])

            self.assertEqual(impact_payload["data"]["changed_paths"], ["src/flash.c"])
            self.assertEqual(
                {item["path"] for item in impact_payload["data"]["likely_propagation"]},
                {"demo/demo_main.c", "src/main.c"},
            )
            self.assertTrue(summary_payload["data"]["risks"])
            self.assertIn("main", summary_payload["data"]["regression_focus"])
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "src/flash.c")
```

Append this to `tests/golden/test_contract_golden.py`:

```python
def test_summarize_impact_payload_matches_golden_fixture(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = build_scope_first_repo(Path(tmpdir))
        with (
            patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
            patch("repo_analysis_tools.impact.service.make_stable_id", side_effect=self._deterministic_make_stable_id),
            patch("repo_analysis_tools.scan.service.datetime") as mock_datetime,
        ):
            mock_datetime.now.return_value = datetime(2026, 4, 19, 3, 13, 48, 74284, tzinfo=timezone.utc)
            scan_repo(str(repo))
            impact_payload = impact_from_paths(str(repo), ["src/flash.c"])
            payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
    assert_matches_fixture(self, "summarize_impact_scope_first.json", self._normalize_repo_paths(payload))
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.integration.test_change_impact_workflow tests.golden.test_contract_golden -v`
Expected: FAIL because the golden fixture does not exist yet and the impact payload shape is not fully wired.

- [ ] **Step 3: Record the deterministic golden fixture**

Create `tests/golden/fixtures/summarize_impact_scope_first.json`:

```json
{
  "schema_version": "1",
  "status": "ok",
  "data": {
    "target_repo": "<repo>",
    "runtime_root": "<repo>/.codewiki",
    "impact_id": "impact_000000000001",
    "scan_id": "scan_000000000001",
    "confirmed_impact": [
      {
        "path": "src/flash.c",
        "anchor_name": null,
        "reason": "changed path",
        "confidence": "confirmed"
      }
    ],
    "likely_propagation": [
      {
        "path": "demo/demo_main.c",
        "anchor_name": "demo_main",
        "reason": "demo_main direct_call flash_init",
        "confidence": "likely"
      },
      {
        "path": "src/main.c",
        "anchor_name": "main",
        "reason": "main direct_call flash_init",
        "confidence": "likely"
      }
    ],
    "regression_focus": ["demo_main", "main"],
    "blind_spots": [
      "Propagation is limited to extracted anchor relations and does not model runtime-only behavior."
    ],
    "risks": [
      {
        "level": "medium",
        "title": "Callers may need regression coverage",
        "summary": "1 changed path(s), 2 likely propagation target(s).",
        "supporting_paths": ["demo/demo_main.c", "src/main.c"],
        "supporting_anchor_names": ["demo_main", "main"],
        "uncertainty": "Propagation is limited to extracted anchor relations and does not model runtime-only behavior."
      }
    ],
    "summary": "1 changed path(s), 2 likely propagation target(s)."
  },
  "messages": [
    {
      "level": "info",
      "text": "impact summary loaded"
    }
  ],
  "recommended_next_tools": ["plan_slice", "build_evidence_pack"]
}
```

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.integration.test_change_impact_workflow tests.golden.test_contract_golden -v`
Expected: PASS with the synthetic workflow and deterministic golden payload green.

- [ ] **Step 5: Commit the workflow and golden coverage**

```bash
git add tests/golden/test_contract_golden.py tests/golden/fixtures/summarize_impact_scope_first.json tests/integration/test_change_impact_workflow.py
git commit -m "test: add change-impact workflow coverage"
```

### Task 4: Validate the Real EasyFlash Change Scenario and Ship the Skill

**Files:**
- Create: `tests/e2e/test_change_impact_easyflash.py`
- Create: `.agents/skills/change-impact/SKILL.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Write the failing real-fixture end-to-end test**

Create `tests/e2e/test_change_impact_easyflash.py`:

```python
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack, read_evidence_pack
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.scan_tools import scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


class ChangeImpactEasyFlashTest(unittest.TestCase):
    def test_port_change_surfaces_easyflash_init_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = materialize_easyflash_repo(Path(tmpdir))
            scan_payload = scan_repo(str(repo))
            impact_payload = impact_from_paths(
                str(repo),
                ["easyflash/port/ef_port.c"],
                scan_payload["data"]["scan_id"],
            )
            summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
            slice_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
            evidence_payload = build_evidence_pack(str(repo), slice_payload["data"]["slice_id"])
            read_payload = read_evidence_pack(str(repo), evidence_payload["data"]["evidence_pack_id"])

            self.assertEqual(impact_payload["data"]["changed_paths"], ["easyflash/port/ef_port.c"])
            self.assertIn(
                "easyflash/src/easyflash.c",
                {item["path"] for item in impact_payload["data"]["likely_propagation"]},
            )
            self.assertIn("easyflash_init", summary_payload["data"]["regression_focus"])
            self.assertEqual(read_payload["data"]["citations"][0]["file_path"], "easyflash/src/easyflash.c")
```

- [ ] **Step 2: Run the end-to-end test and verify it fails**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.e2e.test_change_impact_easyflash -v`
Expected: FAIL until the propagation rules recognize the `easyflash_init -> ef_port_init` relation as likely caller impact.

- [ ] **Step 3: Add the workflow skill and M3 architecture notes**

Write `.agents/skills/change-impact/SKILL.md`:

```md
---
name: change-impact
description: Analyze the effect of changing files or anchors in a C repository using structured MCP impact artifacts.
---

# Change Impact

Use this skill when you need to reason about the consequences of changing files, anchors, or focused areas.

## Required Tool Order

1. Call `refresh_scan`.
2. Call `impact_from_paths` or `impact_from_anchor`.
3. Call `summarize_impact`.
4. Inspect related anchors or build a focused slice.
5. Call `build_evidence_pack`.
6. Call `read_evidence_pack`.
7. Call `open_span` only for cited ranges.

## Output Rules

- Separate `Confirmed impact` from `Likely propagation`.
- Put missing coverage and blind spots under `Uncertainty`.
- Put concrete regression ideas under `Regression focus`.
- Cite file paths and line ranges for every confirmed claim.
- Do not promote likely propagation to certainty without evidence.
```

Append this section to `docs/architecture.md`:

```md
## M3 Change-Impact Workflow

M3 adds persisted impact artifacts under `<target_repo>/.codewiki/impact/`.

The supported change-impact path is:

`refresh_scan -> impact_from_paths / impact_from_anchor -> summarize_impact -> plan_slice -> build_evidence_pack`

Impact outputs must distinguish:

- confirmed direct impact
- likely propagation
- blind spots and uncertainty
- recommended regression focus
```

- [ ] **Step 4: Run the end-to-end test and the docs check**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.e2e.test_change_impact_easyflash tests.unit.test_architecture_docs -v`
Expected: PASS with the EasyFlash scenario and updated docs green.

- [ ] **Step 5: Commit the skill and real-fixture validation**

```bash
git add .agents/skills/change-impact/SKILL.md docs/architecture.md tests/e2e/test_change_impact_easyflash.py
git commit -m "feat: add change-impact workflow skill"
```

### Task 5: Run the Full M3 Verification Suite

**Files:**
- Verify: `src/repo_analysis_tools/impact/`
- Verify: `src/repo_analysis_tools/mcp/contracts/impact.py`
- Verify: `src/repo_analysis_tools/mcp/tools/impact_tools.py`
- Verify: `.agents/skills/change-impact/SKILL.md`
- Verify: `docs/architecture.md`
- Verify: `docs/contracts/mcp-tool-contracts.md`
- Verify: `tests/unit/test_impact_service.py`
- Verify: `tests/contract/test_tool_contracts.py`
- Verify: `tests/golden/test_contract_golden.py`
- Verify: `tests/integration/test_change_impact_workflow.py`
- Verify: `tests/e2e/test_change_impact_easyflash.py`

- [ ] **Step 1: Run the targeted M3 suite**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest tests.unit.test_impact_service tests.contract.test_tool_contracts tests.golden.test_contract_golden tests.integration.test_change_impact_workflow tests.e2e.test_change_impact_easyflash -v`
Expected: PASS with real impact payloads, synthetic workflow coverage, and the EasyFlash scenario all green.

- [ ] **Step 2: Run the full repository suite**

Run: `/home/hyx/anaconda3/envs/agent/bin/python -m unittest discover -s tests -t . -v`
Expected: PASS with M1/M2 coverage preserved and the new M3 tests included.

- [ ] **Step 3: Commit any last-mile adjustments**

```bash
git add src/repo_analysis_tools/impact src/repo_analysis_tools/mcp/contracts/impact.py src/repo_analysis_tools/mcp/tools/impact_tools.py .agents/skills/change-impact/SKILL.md docs/architecture.md docs/contracts/mcp-tool-contracts.md tests/unit/test_impact_service.py tests/contract/test_tool_contracts.py tests/golden tests/integration/test_change_impact_workflow.py tests/e2e/test_change_impact_easyflash.py
git commit -m "feat: deliver M3 change-impact workflow"
```

## Self-Review

- Spec coverage: this plan maps the M3 spec into impact-domain implementation, path and anchor entry points, structured summarization, a workflow skill, and one real EasyFlash change scenario.
- Placeholder scan: no `TODO`, `TBD`, or “similar to above” references remain.
- Type consistency: `impact_id` is used consistently across models, store, service, contracts, tools, golden fixtures, and workflow tests.
