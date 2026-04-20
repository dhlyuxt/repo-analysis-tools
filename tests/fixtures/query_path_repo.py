from pathlib import Path


def build_query_path_repo(
    tmp_path: Path,
    branch_count: int = 2,
    include_dead_end: bool = False,
) -> Path:
    repo = tmp_path / "query-path-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)

    lines = [
        "int helper(void) { return 1; }",
        "",
        "int dst(void) { return helper() + external_api(); }",
    ]
    for index in range(branch_count):
        lines.append(f"int mid_{index}(void) {{ return dst(); }}")
    if include_dead_end:
        lines.append("int dead_end(void) { return helper(); }")

    lines.append("int src(void) {")
    if branch_count == 0 and not include_dead_end:
        lines.append("    return 0;")
    else:
        fanout_terms = [f"mid_{index}()" for index in range(branch_count)]
        if include_dead_end:
            fanout_terms.append("dead_end()")
        lines.append(f"    return {fanout_terms[0]}")
        for term in fanout_terms[1:]:
            lines.append(f"        + {term}")
        lines.append("        ;")
    lines.append("}")

    (repo / "src" / "graph.c").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return repo
