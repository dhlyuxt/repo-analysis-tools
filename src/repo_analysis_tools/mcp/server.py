from repo_analysis_tools.mcp.app import mcp


def _register_tools() -> None:
    from repo_analysis_tools.mcp import tools as registered_tools

    _ = registered_tools


def create_server():
    return mcp


def main() -> None:
    _register_tools()
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
