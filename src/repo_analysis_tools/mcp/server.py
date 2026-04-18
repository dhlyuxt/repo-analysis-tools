from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp import tools as registered_tools


def create_server():
    return mcp


def main() -> None:
    _ = registered_tools
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
