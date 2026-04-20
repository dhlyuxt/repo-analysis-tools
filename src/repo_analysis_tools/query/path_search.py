from __future__ import annotations

from collections import deque


def enumerate_simple_paths(
    adjacency: dict[str, list[tuple[str, int]]],
    start: str,
    goal: str,
    *,
    limit: int,
) -> tuple[list[list[tuple[str, int | None]]], bool]:
    queue: deque[list[tuple[str, int | None]]] = deque([[(start, None)]])
    found: list[list[tuple[str, int | None]]] = []
    overflow_found = False

    while queue and not overflow_found:
        path = queue.popleft()
        node = path[-1][0]
        if node == goal:
            if len(found) < limit:
                found.append(path)
            else:
                overflow_found = True
            continue

        visited = {item[0] for item in path}
        for next_node, line in adjacency.get(node, []):
            if next_node in visited:
                continue
            queue.append(path + [(next_node, line)])

    return found, overflow_found
