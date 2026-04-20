from __future__ import annotations

from collections.abc import Mapping
from heapq import heappop, heappush


def _path_sort_key(
    path: tuple[tuple[str, int | None], ...],
    node_sort_keys: Mapping[str, tuple[str, str]],
) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    names = tuple(node_sort_keys[node_id][0] for node_id, _ in path)
    symbol_ids = tuple(node_sort_keys[node_id][1] for node_id, _ in path)
    return len(path) - 1, names, symbol_ids


def enumerate_simple_paths(
    adjacency: dict[str, list[tuple[str, int]]],
    start: str,
    goal: str,
    *,
    limit: int,
    node_sort_keys: Mapping[str, tuple[str, str]] | None = None,
) -> tuple[list[list[tuple[str, int | None]]], bool]:
    sort_keys = dict(node_sort_keys or {})
    for node_id, edges in adjacency.items():
        sort_keys.setdefault(node_id, (node_id, node_id))
        for next_node, _ in edges:
            sort_keys.setdefault(next_node, (next_node, next_node))
    sort_keys.setdefault(start, (start, start))
    sort_keys.setdefault(goal, (goal, goal))

    initial_path = ((start, None),)
    queue: list[tuple[tuple[int, tuple[str, ...], tuple[str, ...]], tuple[tuple[str, int | None], ...]]] = []
    heappush(queue, (_path_sort_key(initial_path, sort_keys), initial_path))
    found: list[list[tuple[str, int | None]]] = []
    truncated = False

    while queue:
        _, path = heappop(queue)
        node = path[-1][0]
        if node == goal:
            if len(found) < limit:
                found.append(list(path))
            else:
                truncated = True
                break

        visited = {item[0] for item in path}
        for next_node, line in adjacency.get(node, []):
            if next_node in visited:
                continue
            next_path = path + ((next_node, line),)
            heappush(queue, (_path_sort_key(next_path, sort_keys), next_path))

    return found, truncated
