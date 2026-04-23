import unittest

from repo_analysis_tools.query.path_search import enumerate_simple_paths


class _TrackingAdjacency(dict):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.requested_nodes: list[str] = []

    def get(self, key, default=None):
        self.requested_nodes.append(key)
        return super().get(key, default)


class QueryPathSearchTest(unittest.TestCase):
    def test_enumeration_stops_expanding_after_reaching_goal(self) -> None:
        adjacency = _TrackingAdjacency(
            {
                "start": [("goal", 1)],
                "goal": [(f"post_{index}", index) for index in range(20)],
            }
        )

        found, truncated = enumerate_simple_paths(adjacency, "start", "goal", limit=8)

        self.assertEqual(found, [[("start", None), ("goal", 1)]])
        self.assertFalse(truncated)
        self.assertEqual(adjacency.requested_nodes, ["start"])
