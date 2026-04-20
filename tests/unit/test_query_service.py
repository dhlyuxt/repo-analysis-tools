import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.query.service import QueryService
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.query_repo import build_query_repo
from tests.fixtures.query_path_repo import build_query_path_repo


class QueryServiceTest(unittest.TestCase):
    def test_file_queries_and_symbol_queries_return_structured_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            priority_files = service.list_priority_files(repo, scan_snapshot.scan_id)
            file_info = service.get_file_info(repo, scan_snapshot.scan_id, "src/main.c")
            file_symbols = service.list_file_symbols(
                repo,
                scan_snapshot.scan_id,
                ["src/main.c", "src/flash.c"],
            )
            file_symbol_map = {row.path: row.symbols for row in file_symbols}
            symbol_matches = service.resolve_symbols(repo, scan_snapshot.scan_id, "flash_init")
            symbol_id = symbol_matches.matches[0].symbol_id
            symbol_context = service.open_symbol_context(repo, scan_snapshot.scan_id, symbol_id, 1)

            self.assertEqual(priority_files[0].path, "src/main.c")
            self.assertEqual(file_info.path, "src/main.c")
            self.assertTrue(file_info.has_main_definition)
            self.assertEqual(file_info.symbol_count, 2)
            self.assertEqual(symbol_matches.match_count, 2)
            self.assertEqual(symbol_matches.matches[0].kind, "function")
            self.assertEqual(symbol_context.definition_line_start, 2)
            self.assertIn("flash init comment", "\n".join(symbol_context.lines))
            self.assertEqual(
                {symbol.name for symbol in file_symbol_map["src/flash.c"]},
                {"flash_init", "helper"},
            )

    def test_open_symbol_context_prefers_definition_for_declaration_symbol_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            file_symbols = service.list_file_symbols(repo, scan_snapshot.scan_id, ["src/main.c"])
            declaration_symbol = next(symbol for symbol in file_symbols[0].symbols if symbol.name == "flash_init")

            symbol_context = service.open_symbol_context(
                repo,
                scan_snapshot.scan_id,
                declaration_symbol.symbol_id,
                0,
            )

            self.assertEqual(symbol_context.path, "src/flash.c")
            self.assertEqual(symbol_context.definition_line_start, 2)
            self.assertEqual(symbol_context.definition_line_end, 4)
            self.assertTrue(symbol_context.lines[0].startswith("int flash_init(void)"))
            self.assertEqual(symbol_context.lines[-1], "}")
            self.assertNotIn("int flash_init(void);", "\n".join(symbol_context.lines))

    def test_resolve_symbols_does_not_return_substring_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            symbol_matches = service.resolve_symbols(repo, scan_snapshot.scan_id, "flash")

            self.assertEqual(symbol_matches.match_count, 0)
            self.assertEqual(symbol_matches.matches, ())

    def test_open_symbol_context_ignores_braces_inside_strings_and_comments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            weird_symbol = service.resolve_symbols(repo, scan_snapshot.scan_id, "weird").matches[0]
            symbol_context = service.open_symbol_context(repo, scan_snapshot.scan_id, weird_symbol.symbol_id, 0)

            self.assertEqual(symbol_context.path, "src/weird.c")
            self.assertEqual(symbol_context.definition_line_start, 1)
            self.assertEqual(symbol_context.definition_line_end, 5)
            self.assertEqual(symbol_context.lines[-1], "}")
            self.assertIn('const char *s = "}";', symbol_context.lines[1])

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
            self.assertEqual({row.name for row in relations.callees}, {"helper"})
            self.assertEqual({row.name for row in relations.non_resolved_callees}, {"external_api"})
            self.assertEqual({row.name for row in roots}, {"src"})
            self.assertEqual(paths.status, "truncated")
            self.assertEqual(paths.returned_path_count, 8)
            self.assertTrue(paths.truncated)
            self.assertEqual(paths.paths[0].hop_count, 2)
            self.assertEqual(paths.paths[0].nodes[0].name, "src")
            self.assertEqual(paths.paths[0].nodes[-1].name, "dst")

    def test_find_call_paths_does_not_truncate_when_only_dead_end_paths_remain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_path_repo(Path(tmpdir), branch_count=8, include_dead_end=True)
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            src_id = service.resolve_symbols(repo, scan_snapshot.scan_id, "src").matches[0].symbol_id
            dst_id = service.resolve_symbols(repo, scan_snapshot.scan_id, "dst").matches[0].symbol_id

            paths = service.find_call_paths(repo, scan_snapshot.scan_id, src_id, dst_id)

            self.assertEqual(paths.status, "found")
            self.assertFalse(paths.truncated)
            self.assertEqual(paths.returned_path_count, 8)

    def test_query_call_relations_rejects_non_function_symbol_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            file_symbols = service.list_file_symbols(repo, scan_snapshot.scan_id, ["include/types.h"])
            non_function_symbol = file_symbols[0].symbols[0]

            with self.assertRaisesRegex(ValueError, "must reference a function"):
                service.query_call_relations(repo, scan_snapshot.scan_id, non_function_symbol.symbol_id)

    def test_find_call_paths_rejects_non_function_symbol_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = build_query_repo(Path(tmpdir))
            scan_snapshot = ScanService().scan(repo)
            service = QueryService()

            file_symbols = service.list_file_symbols(repo, scan_snapshot.scan_id, ["include/types.h"])
            non_function_symbol = file_symbols[0].symbols[0]
            src_id = service.resolve_symbols(repo, scan_snapshot.scan_id, "main").matches[0].symbol_id

            with self.assertRaisesRegex(ValueError, "must reference a function"):
                service.find_call_paths(
                    repo,
                    scan_snapshot.scan_id,
                    non_function_symbol.symbol_id,
                    src_id,
                )
