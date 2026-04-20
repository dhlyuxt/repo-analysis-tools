import tempfile
import unittest
from pathlib import Path

from repo_analysis_tools.query.service import QueryService
from repo_analysis_tools.scan.service import ScanService
from tests.fixtures.query_repo import build_query_repo


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
                1,
            )

            self.assertEqual(symbol_context.path, "src/flash.c")
            self.assertEqual(symbol_context.definition_line_start, 2)
            self.assertEqual(symbol_context.definition_line_end, 3)
            self.assertIn("flash init comment", symbol_context.lines[0])
            self.assertNotIn("int flash_init(void);", "\n".join(symbol_context.lines))
