from __future__ import annotations

import os
import queue
import sys
import threading
from contextlib import asynccontextmanager
from io import TextIOWrapper

import anyio
import anyio.lowlevel
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

import mcp.types as types
from mcp.shared.message import SessionMessage

DEBUG_ENV = "REPO_ANALYSIS_TOOLS_STDIO_DEBUG"


def _debug(message: str) -> None:
    if not os.environ.get(DEBUG_ENV):
        return
    sys.stderr.write(f"[repo-analysis-stdio] {message}\n")
    sys.stderr.flush()


@asynccontextmanager
async def blocking_stdio_server(
    stdin: TextIOWrapper | None = None,
    stdout: TextIOWrapper | None = None,
):
    """Stdio transport that uses blocking readline()/write() inside worker threads.

    The upstream AnyIO file wrapper path does not yield lines reliably for stdin pipes
    in this environment, so we bridge the protocol with explicit blocking I/O.
    """

    stdin = stdin or TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    stdout = stdout or TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    read_stream: MemoryObjectReceiveStream[SessionMessage | Exception]
    read_stream_writer: MemoryObjectSendStream[SessionMessage | Exception]
    write_stream: MemoryObjectSendStream[SessionMessage]
    write_stream_reader: MemoryObjectReceiveStream[SessionMessage]

    read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(0)
    stop_event = threading.Event()
    read_queue: queue.Queue[SessionMessage | Exception | None] = queue.Queue()
    write_queue: queue.Queue[str | None] = queue.Queue()

    def stdin_reader() -> None:
        try:
            while not stop_event.is_set():
                line = stdin.readline()
                if line == "":
                    _debug("stdin EOF")
                    read_queue.put(None)
                    break
                _debug(f"stdin line: {line.rstrip()}")
                try:
                    message = types.JSONRPCMessage.model_validate_json(line)
                except Exception as exc:
                    _debug(f"stdin parse error: {exc!r}")
                    read_queue.put(exc)
                    continue

                read_queue.put(SessionMessage(message))
        except Exception as exc:  # pragma: no cover
            read_queue.put(exc)

    def stdout_writer() -> None:
        while True:
            payload = write_queue.get()
            if payload is None:
                _debug("stdout sentinel")
                break
            _debug(f"stdout line: {payload}")
            stdout.write(payload + "\n")
            stdout.flush()

    async def stdin_pump() -> None:
        try:
            async with read_stream_writer:
                while True:
                    try:
                        item = read_queue.get_nowait()
                    except queue.Empty:
                        await anyio.sleep(0.001)
                        continue
                    if item is None:
                        break
                    await read_stream_writer.send(item)
        except anyio.ClosedResourceError:  # pragma: no cover
            await anyio.lowlevel.checkpoint()

    async def stdout_pump() -> None:
        try:
            async with write_stream_reader:
                async for session_message in write_stream_reader:
                    payload = session_message.message.model_dump_json(by_alias=True, exclude_none=True)
                    write_queue.put(payload)
        except anyio.ClosedResourceError:  # pragma: no cover
            await anyio.lowlevel.checkpoint()
        finally:
            write_queue.put(None)

    stdin_thread = threading.Thread(target=stdin_reader, name="repo-analysis-stdin-reader", daemon=True)
    stdout_thread = threading.Thread(target=stdout_writer, name="repo-analysis-stdout-writer", daemon=True)
    stdin_thread.start()
    stdout_thread.start()
    async with anyio.create_task_group() as tg:
        tg.start_soon(stdin_pump)
        tg.start_soon(stdout_pump)
        try:
            yield read_stream, write_stream
        finally:
            stop_event.set()
            write_queue.put(None)
            stdin_thread.join(timeout=0.1)
            stdout_thread.join(timeout=0.1)
