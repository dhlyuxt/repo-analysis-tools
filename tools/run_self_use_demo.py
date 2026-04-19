from __future__ import annotations

import json
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Callable
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from repo_analysis_tools.mcp.tools.evidence_tools import build_evidence_pack
from repo_analysis_tools.mcp.tools.export_tools import export_analysis_bundle
from repo_analysis_tools.mcp.tools.impact_tools import impact_from_paths, summarize_impact
from repo_analysis_tools.mcp.tools.report_tools import render_module_summary
from repo_analysis_tools.mcp.tools.scan_tools import refresh_scan, scan_repo
from repo_analysis_tools.mcp.tools.slice_tools import plan_slice
from tests.fixtures.easyflash_repo import materialize_easyflash_repo


def _deterministic_stable_id_factory() -> Callable[[object], str]:
    counters = {
        "scan": 0,
        "slice": 0,
        "evidence_pack": 0,
        "impact": 0,
        "report": 0,
        "export": 0,
    }

    def _next(kind) -> str:
        counters[kind.value] += 1
        return f"{kind.value}_{counters[kind.value]:012x}"

    return _next


def run_demo() -> dict[str, object]:
    repo = materialize_easyflash_repo(Path(tempfile.mkdtemp(prefix="self-use-demo-")))
    with ExitStack() as stack:
        deterministic_make_stable_id = _deterministic_stable_id_factory()
        stack.enter_context(
            patch("repo_analysis_tools.scan.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )
        stack.enter_context(
            patch("repo_analysis_tools.slice.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )
        stack.enter_context(
            patch("repo_analysis_tools.evidence.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )
        stack.enter_context(
            patch("repo_analysis_tools.impact.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )
        stack.enter_context(
            patch("repo_analysis_tools.report.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )
        stack.enter_context(
            patch("repo_analysis_tools.export.service.make_stable_id", side_effect=deterministic_make_stable_id)
        )

        scan_payload = scan_repo(str(repo))
        refresh_payload = refresh_scan(str(repo), scan_payload["data"]["scan_id"])
        latest_scan_id = refresh_payload["data"]["scan_id"]
        plan_payload = plan_slice(str(repo), "Where is easyflash_init defined?")
        evidence_payload = build_evidence_pack(str(repo), plan_payload["data"]["slice_id"])
        impact_payload = impact_from_paths(
            str(repo),
            ["easyflash/src/easyflash.c"],
            latest_scan_id,
        )
        summary_payload = summarize_impact(str(repo), impact_payload["data"]["impact_id"])
        report_payload = render_module_summary(
            str(repo),
            evidence_payload["data"]["evidence_pack_id"],
            "easyflash",
        )
        export_payload = export_analysis_bundle(str(repo), report_payload["data"]["report_id"])

    return {
        "repo_root": str(repo),
        "scan_id": latest_scan_id,
        "evidence_pack_id": evidence_payload["data"]["evidence_pack_id"],
        "impact_id": impact_payload["data"]["impact_id"],
        "report_id": report_payload["data"]["report_id"],
        "export_id": export_payload["data"]["export_id"],
        "markdown_path": report_payload["data"]["markdown_path"],
        "copied_markdown_path": export_payload["data"]["copied_markdown_path"],
        "summary": summary_payload["data"]["summary"],
    }


def main() -> int:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
