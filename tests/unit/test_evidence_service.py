import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.evidence.models import CitationRecord
from repo_analysis_tools.evidence.service import EvidenceService, MAX_OPEN_SPAN_LINES
from repo_analysis_tools.evidence.snippets import read_snippet
from repo_analysis_tools.scan.service import ScanService
from repo_analysis_tools.slice.service import SliceService
from tests.fixtures.scope_first_repo import build_scope_first_repo


class EvidenceServiceTest(unittest.TestCase):
    def test_build_and_read_persist_real_citations_from_slice_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            service = EvidenceService()

            built = service.build(repo, slice_manifest.slice_id)
            loaded = service.read(repo, built.evidence_pack_id)

            self.assertEqual(built.slice_id, slice_manifest.slice_id)
            self.assertEqual(built.scan_id, scan_snapshot.scan_id)
            self.assertEqual(built.citation_count, 1)
            self.assertEqual(
                [
                    (citation.file_path, citation.anchor_name, citation.line_start, citation.line_end)
                    for citation in built.citations
                ],
                [("src/flash.c", "flash_init", 1, 1)],
            )
            self.assertEqual(loaded.evidence_pack_id, built.evidence_pack_id)
            self.assertEqual(loaded.summary, built.summary)
            self.assertEqual(
                [citation.file_path for citation in loaded.citations],
                ["src/flash.c"],
            )

    def test_open_span_reads_lines_when_request_is_inside_citation_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            service = EvidenceService()
            evidence_pack = service.build(repo, slice_manifest.slice_id)

            opened = service.open_span(repo, evidence_pack.evidence_pack_id, "src/flash.c", 1, 1)

            self.assertEqual(opened.path, "src/flash.c")
            self.assertEqual(opened.line_start, 1)
            self.assertEqual(opened.line_end, 1)
            self.assertEqual(opened.lines, ["int flash_init(void) { return 0; }"])

    def test_open_span_rejects_requests_outside_evidence_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            service = EvidenceService()
            evidence_pack = service.build(repo, slice_manifest.slice_id)

            with self.assertRaisesRegex(ValueError, "fully covered by an evidence citation"):
                service.open_span(repo, evidence_pack.evidence_pack_id, "src/flash.c", 1, 2)

    def test_open_span_rejects_windows_larger_than_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "snippet-repo"
            (repo / "src").mkdir(parents=True, exist_ok=True)
            (repo / "src" / "large.c").write_text(
                "".join(f"line {index}\n" for index in range(1, MAX_OPEN_SPAN_LINES + 3)),
                encoding="utf-8",
            )
            service = EvidenceService()

            with self.assertRaisesRegex(ValueError, str(MAX_OPEN_SPAN_LINES)):
                service._validate_open_span_request(
                    citations=[
                        CitationRecord(
                            file_path="src/large.c",
                            anchor_name="large",
                            kind="function_definition",
                            line_start=1,
                            line_end=MAX_OPEN_SPAN_LINES + 2,
                        )
                    ],
                    path="src/large.c",
                    line_start=1,
                    line_end=MAX_OPEN_SPAN_LINES + 1,
                )

    def test_build_rejects_drifted_selected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_scope_first_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            slice_manifest = SliceService().plan(repo, "Where is flash_init defined?", scan_snapshot.scan_id)
            (repo / "src" / "flash.c").write_text("int flash_init(void) { return 7; }\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "drifted"):
                EvidenceService().build(repo, slice_manifest.slice_id)

    def test_read_snippet_falls_back_to_gb18030(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "encoding-repo"
            (repo / "src").mkdir(parents=True, exist_ok=True)
            (repo / "src" / "legacy.txt").write_bytes("你好，世界\n第二行\n".encode("gb18030"))

            lines = read_snippet(repo, "src/legacy.txt", 1, 2)

            self.assertEqual(lines, ["你好，世界", "第二行"])
