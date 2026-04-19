from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ScopeConfig:
    focus_roots: tuple[str, ...]
    external_roots: tuple[str, ...]
    ignore_roots: tuple[str, ...]
    include_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]


class ScopeConfigLoader:
    DEFAULTS: ClassVar[dict[str, tuple[str, ...]]] = {
        "focus_roots": ("src",),
        "external_roots": ("vendor", "third_party", "demo"),
        "ignore_roots": ("build", "generated"),
        "include_globs": ("*.c", "*.h", "**/*.c", "**/*.h"),
        "exclude_globs": ("**/tests/**",),
    }

    def load(self, target_repo: str | None = None) -> ScopeConfig:
        del target_repo
        return ScopeConfig(**self.DEFAULTS)
