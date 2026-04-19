from pathlib import Path


def build_scope_first_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "scope-first-repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "ports").mkdir(parents=True, exist_ok=True)
    (repo / "demo").mkdir(parents=True, exist_ok=True)
    (repo / "generated").mkdir(parents=True, exist_ok=True)

    (repo / "src" / "main.c").write_text(
        '#include "config.h"\n'
        "int flash_init(void);\n"
        "int main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "src" / "flash.c").write_text(
        "int flash_init(void) { return 0; }\n",
        encoding="utf-8",
    )
    (repo / "src" / "config.h").write_text(
        "#define EF_USING_ENV 1\n",
        encoding="utf-8",
    )
    (repo / "ports" / "board_port.c").write_text(
        "void board_port_init(void) {}\n",
        encoding="utf-8",
    )
    (repo / "demo" / "demo_main.c").write_text(
        "int flash_init(void);\n"
        "int demo_main(void) { return flash_init(); }\n",
        encoding="utf-8",
    )
    (repo / "generated" / "autoconf.h").write_text(
        "#define GENERATED_VALUE 1\n",
        encoding="utf-8",
    )
    return repo
