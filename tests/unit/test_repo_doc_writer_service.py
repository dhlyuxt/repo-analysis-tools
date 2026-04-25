import json
import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.report.repo_design_models import RepositoryFindingsPackage
from repo_analysis_tools.report.repo_design_service import RepositoryDesignWriter


def sample_payload(output_root: str) -> dict[str, object]:
    citation = {
        "file_path": "docs/architecture.md",
        "line_start": 1,
        "line_end": 120,
        "symbol_name": "repo_design",
    }
    return {
        "repo_name": "demo-repo",
        "target_repo": "/tmp/demo-repo",
        "output_root": output_root,
        "module_map": [
            {
                "module_id": "core",
                "module_name": "Core",
                "responsibility": "Coordinates repository analysis requests.",
                "paths": ["src/core.py"],
                "dependencies": ["storage"],
            },
            {
                "module_id": "storage",
                "module_name": "Storage",
                "responsibility": "Persists repository analysis artifacts.",
                "paths": ["src/storage.py"],
                "dependencies": [],
            },
        ],
        "module_reports": [
            {
                "module_id": "core",
                "summary": ["Core turns user requests into analysis work."],
                "entry_points": ["analyze_repository"],
                "key_symbols": ["RepositoryAnalyzer"],
                "call_flows": ["analyze_repository -> save_manifest"],
                "risks": ["Request orchestration depends on storage availability."],
                "unknowns": ["Runtime concurrency limits are not represented."],
                "citations": [citation],
            },
            {
                "module_id": "storage",
                "summary": ["Storage writes artifacts to disk."],
                "entry_points": ["save_manifest"],
                "key_symbols": ["ManifestStore"],
                "call_flows": ["save_manifest -> write_json"],
                "risks": ["Disk write failures need caller handling."],
                "unknowns": [],
                "citations": [citation],
            },
        ],
        "global_findings": {
            "architecture_summary": [
                "The repository separates orchestration from persistence."
            ],
            "cross_module_flows": ["core -> storage"],
            "constraints": ["Generated documentation must be deterministic."],
            "unknowns": ["Deployment topology is not described."],
            "citations": [citation],
        },
    }


class RepositoryDesignWriterTest(unittest.TestCase):
    def test_sample_payload_writes_required_files_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = str(Path(tmpdir) / "docs" / "repo-design")
            package = RepositoryFindingsPackage.from_dict(sample_payload(output_root))

            manifest = RepositoryDesignWriter().write_document_set(package)

            expected_paths = {
                "index.md",
                "repository-architecture.md",
                "module-map.md",
                "evidence-index.md",
                "modules/core.md",
                "modules/storage.md",
            }
            self.assertEqual(expected_paths, {doc.relative_path for doc in manifest.documents})
            self.assertEqual("ok", manifest.validation_status)
            self.assertEqual(2, manifest.unknown_count)

            for relative_path in expected_paths:
                self.assertTrue((Path(output_root) / relative_path).is_file(), relative_path)

            manifest_payload = json.loads(
                (Path(output_root) / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual("ok", manifest_payload["validation_status"])
            self.assertEqual(output_root, manifest_payload["output_root"])

            architecture = (Path(output_root) / "repository-architecture.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("```mermaid", architecture)
            self.assertIn("`docs/architecture.md:1-120`", architecture)
            self.assertNotIn("['", architecture)

            core_detail = (Path(output_root) / "modules" / "core.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("- Core turns user requests into analysis work.", core_detail)
            self.assertNotIn("['", core_detail)

    def test_payload_without_global_constraints_writes_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = str(Path(tmpdir) / "docs" / "repo-design")
            payload = sample_payload(output_root)
            payload["global_findings"].pop("constraints")  # type: ignore[union-attr]

            package = RepositoryFindingsPackage.from_dict(payload)
            manifest = RepositoryDesignWriter().write_document_set(package)

            self.assertEqual("ok", manifest.validation_status)
            architecture = (Path(output_root) / "repository-architecture.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("No constraints reported.", architecture)

    def test_empty_modules_and_flows_still_write_valid_mermaid_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = str(Path(tmpdir) / "docs")
            payload = sample_payload(output_root)
            payload["module_map"] = []
            payload["module_reports"] = []
            payload["global_findings"]["cross_module_flows"] = []  # type: ignore[index]
            package = RepositoryFindingsPackage.from_dict(payload)

            manifest = RepositoryDesignWriter().write_document_set(package)

            self.assertEqual("ok", manifest.validation_status)
            self.assertTrue((Path(output_root) / "repository-architecture.md").is_file())
            module_map = (Path(output_root) / "module-map.md").read_text(encoding="utf-8")
            self.assertIn('Empty["No modules reported"]', module_map)

    def test_missing_required_top_level_field_fails_fast(self) -> None:
        payload = sample_payload("/tmp/out")
        payload.pop("repo_name")

        with self.assertRaisesRegex(ValueError, "repo_name"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_summary_fields_must_be_lists(self) -> None:
        payload = sample_payload("/tmp/out")
        payload["module_reports"][0]["summary"] = "not a list"  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "summary must be a list"):
            RepositoryFindingsPackage.from_dict(payload)

        payload = sample_payload("/tmp/out")
        payload["global_findings"]["architecture_summary"] = "not a list"  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "architecture_summary must be a list"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_module_ids_must_be_safe_slugs(self) -> None:
        payload = sample_payload("/tmp/out")
        payload["module_map"][0]["module_id"] = "../escaped"  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "module_id"):
            RepositoryFindingsPackage.from_dict(payload)

        payload = sample_payload("/tmp/out")
        payload["module_reports"][0]["module_id"] = "nested/name"  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "module_id"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_rejects_duplicate_module_map_ids(self) -> None:
        payload = sample_payload("/tmp/out")
        duplicate = dict(payload["module_map"][0])  # type: ignore[index]
        payload["module_map"] = list(payload["module_map"]) + [duplicate]  # type: ignore[arg-type]

        with self.assertRaisesRegex(ValueError, "duplicate module_map module_id: core"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_rejects_duplicate_module_report_ids(self) -> None:
        payload = sample_payload("/tmp/out")
        duplicate = dict(payload["module_reports"][0])  # type: ignore[index]
        payload["module_reports"] = list(payload["module_reports"]) + [duplicate]  # type: ignore[arg-type]

        with self.assertRaisesRegex(ValueError, "duplicate module_reports module_id: core"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_string_lists_reject_non_string_items(self) -> None:
        payload = sample_payload("/tmp/out")
        payload["module_reports"][0]["summary"] = [{"text": "bad"}]  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "summary items must be strings"):
            RepositoryFindingsPackage.from_dict(payload)

        payload = sample_payload("/tmp/out")
        payload["module_reports"][0]["call_flows"] = [123]  # type: ignore[index]

        with self.assertRaisesRegex(ValueError, "call_flows items must be strings"):
            RepositoryFindingsPackage.from_dict(payload)

    def test_rejects_missing_module_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = sample_payload(str(Path(tmpdir) / "docs"))
            payload["module_reports"] = payload["module_reports"][:1]  # type: ignore[index]
            package = RepositoryFindingsPackage.from_dict(payload)

            with self.assertRaisesRegex(ValueError, "missing module_reports.*storage"):
                RepositoryDesignWriter().write_document_set(package)

    def test_rejects_orphan_module_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = sample_payload(str(Path(tmpdir) / "docs"))
            orphan_report = dict(payload["module_reports"][0])  # type: ignore[index]
            orphan_report["module_id"] = "orphan"
            payload["module_reports"] = list(payload["module_reports"]) + [orphan_report]  # type: ignore[arg-type]
            package = RepositoryFindingsPackage.from_dict(payload)

            with self.assertRaisesRegex(ValueError, "orphan module_reports.*orphan"):
                RepositoryDesignWriter().write_document_set(package)
