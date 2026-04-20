from pathlib import Path


def build_query_path_repo(tmp_path: Path, branch_count: int = 2) -> Path:
    repo = tmp_path / "query-path-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)

    lines = [
        "int helper(void) { return 1; }",
        "",
        "int dst(void) { return helper() + external_api(); }",
    ]
    for index in range(branch_count):
        lines.append(f"int mid_{index}(void) {{ return dst(); }}")
    fanout = " + ".join(f"mid_{index}()" for index in range(branch_count)) or "0"
    lines.append(f"int src(void) {{ return {fanout}; }}")

    (repo / "src" / "graph.c").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return repo
