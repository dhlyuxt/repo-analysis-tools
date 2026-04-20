from pathlib import Path


def build_query_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "query-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "include").mkdir(parents=True, exist_ok=True)
    (repo / "ports").mkdir(parents=True, exist_ok=True)

    (repo / "src" / "main.c").write_text(
        '#include "types.h"\n'
        "int flash_init(void);\n"
        "int main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "flash.c").write_text(
        "/* flash init comment */\n"
        "int flash_init(void) {\n"
        "    return helper();\n"
        "}\n"
        "static int helper(void) { return 1; }\n",
        encoding="utf-8",
    )
    (repo / "include" / "types.h").write_text(
        "typedef struct flash_cfg {\n"
        "    int enabled;\n"
        "} flash_cfg;\n",
        encoding="utf-8",
    )
    (repo / "ports" / "flash_port.c").write_text(
        "int flash_port_init(void) { return 0; }\n",
        encoding="utf-8",
    )
    return repo
