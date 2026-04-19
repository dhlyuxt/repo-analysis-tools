import anyio

from repo_analysis_tools.mcp.app import mcp
from repo_analysis_tools.mcp.stdio_transport import blocking_stdio_server


def _register_tools() -> None:
    from repo_analysis_tools.mcp import tools as registered_tools

    _ = registered_tools


def create_server():
    return mcp


async def run_stdio_server() -> None:
    _register_tools()
    server = create_server()
    async with blocking_stdio_server() as (read_stream, write_stream):
        await server._mcp_server.run(
            read_stream,
            write_stream,
            server._mcp_server.create_initialization_options(),
        )


def main() -> None:
    anyio.run(run_stdio_server)


if __name__ == "__main__":
    main()
