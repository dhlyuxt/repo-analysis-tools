from __future__ import annotations

from collections import defaultdict
from pathlib import Path, PurePosixPath
import re

from repo_analysis_tools.scan.models import ScannedFile
from repo_analysis_tools.scan.store import ScanStore
from repo_analysis_tools.scope.config import ScopeConfig, ScopeConfigLoader
from repo_analysis_tools.scope.models import ScopeNode, ScopeSnapshot, ScopedFile
from repo_analysis_tools.scope.store import ScopeStore


class ScopeService:
    PRIMARY_HINTS = {"src", "source", "lib", "include", "app", "core"}
    SUPPORT_HINTS = {"ports", "port", "board", "bsp", "platform", "hal", "support"}
    EXTERNAL_HINTS = {"demo", "vendor", "third_party", "third-party", "examples"}
    GENERATED_HINTS = {"generated", "autogen", "gen"}
    ROLE_ORDER = ("primary", "support", "external", "generated")

    def __init__(self, config_loader: ScopeConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ScopeConfigLoader()

    def build_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> ScopeSnapshot:
        repo = Path(target_repo).expanduser().resolve()
        scan_snapshot = ScanStore.for_repo(repo).load(scan_id=scan_id)
        config = self.config_loader.load(str(repo))
        scoped_files = self._classify_files(scan_snapshot.files, config)
        nodes = self._build_nodes(scoped_files)
        snapshot = ScopeSnapshot(
            scan_id=scan_snapshot.scan_id,
            repo_root=scan_snapshot.repo_root,
            scope_summary=self._build_scope_summary(nodes, scoped_files),
            role_counts=self._build_role_counts(scoped_files),
            nodes=nodes,
            files=scoped_files,
        )
        ScopeStore.for_repo(repo).save(snapshot)
        return snapshot

    def load_snapshot(self, target_repo: Path | str, scan_id: str | None = None) -> ScopeSnapshot:
        return ScopeStore.for_repo(target_repo).load(scan_id=scan_id)

    def explain_node(self, target_repo: Path | str, node_id: str, scan_id: str | None = None) -> ScopeNode:
        snapshot = self.load_snapshot(target_repo, scan_id=scan_id)
        for node in snapshot.nodes:
            if node.node_id == node_id:
                return node
        raise FileNotFoundError(f"scope node {node_id} was not found")

    def _classify_files(self, scanned_files: list[ScannedFile], config: ScopeConfig) -> list[ScopedFile]:
        scoped_files: list[ScopedFile] = []
        for scanned_file in sorted(scanned_files, key=lambda item: item.path):
            if not self._is_included(scanned_file.path, config):
                continue
            label = self._node_label(scanned_file.path)
            scoped_files.append(
                ScopedFile(
                    path=scanned_file.path,
                    role=self._classify_role(scanned_file.path, config),
                    node_id=self._node_id(label),
                )
            )
        return scoped_files

    def _is_included(self, relative_path: str, config: ScopeConfig) -> bool:
        path = PurePosixPath(relative_path)
        if any(path.match(pattern) for pattern in config.exclude_globs):
            return False
        if any(path.match(pattern) for pattern in config.include_globs):
            return True
        return False

    def _classify_role(self, relative_path: str, config: ScopeConfig) -> str:
        parts = PurePosixPath(relative_path).parts
        root = parts[0].lower() if parts else ""
        tokens = self._tokens(relative_path)
        if root in config.ignore_roots or self.GENERATED_HINTS & tokens:
            return "generated"
        if root in config.external_roots or self.EXTERNAL_HINTS & tokens:
            return "external"
        if root in config.focus_roots:
            return "primary"
        if self.SUPPORT_HINTS & tokens:
            return "support"
        if self.PRIMARY_HINTS & tokens:
            return "primary"
        return "primary"

    def _tokens(self, relative_path: str) -> set[str]:
        return {
            token
            for token in re.split(r"[/_.-]+", relative_path.lower())
            if token
        }

    def _node_label(self, relative_path: str) -> str:
        parts = PurePosixPath(relative_path).parts
        if not parts:
            return "root"
        return parts[0]

    def _node_id(self, label: str) -> str:
        if not label:
            return "scope_root"
        encoded = "".join(
            character
            if character.isascii() and character.isalnum()
            else f"_x{ord(character):02x}_"
            for character in label
        )
        return f"scope_{encoded}"

    def _build_nodes(self, scoped_files: list[ScopedFile]) -> list[ScopeNode]:
        related_files_by_node: dict[str, list[str]] = defaultdict(list)
        label_by_node: dict[str, str] = {}
        role_by_node: dict[str, str] = {}
        for scoped_file in scoped_files:
            related_files_by_node[scoped_file.node_id].append(scoped_file.path)
            label_by_node[scoped_file.node_id] = self._node_label(scoped_file.path)
            role_by_node.setdefault(scoped_file.node_id, scoped_file.role)
        nodes = [
            ScopeNode(
                node_id=node_id,
                label=label_by_node[node_id],
                role=role_by_node[node_id],
                file_count=len(sorted(paths)),
                related_files=sorted(paths),
            )
            for node_id, paths in related_files_by_node.items()
        ]
        return sorted(nodes, key=lambda node: node.label)

    def _build_role_counts(self, scoped_files: list[ScopedFile]) -> dict[str, int]:
        counts = {role: 0 for role in self.ROLE_ORDER}
        for scoped_file in scoped_files:
            counts[scoped_file.role] += 1
        return {
            role: count
            for role, count in counts.items()
            if count > 0
        }

    def _build_scope_summary(self, nodes: list[ScopeNode], scoped_files: list[ScopedFile]) -> str:
        roles = [role for role in self.ROLE_ORDER if any(node.role == role for node in nodes)]
        if not roles:
            return "0 scope nodes cover 0 files."
        if len(roles) == 1:
            role_text = roles[0]
        else:
            role_text = ", ".join(roles[:-1]) + f", and {roles[-1]}"
        return f"{len(nodes)} scope nodes cover {len(scoped_files)} files across {role_text} roles."
