from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ServerSettings:
    enable_diagnostics: bool = True
    enable_completion: bool = True
    enable_hover: bool = True
    enable_definition: bool = True
    enable_references: bool = True
    enable_document_symbols: bool = True
    enable_jedi: bool = True
    enable_sage_bridge: bool = True
    enable_ruff: bool = True
    enable_ty: bool = True
    max_completion_items: int = 120
    ruff_command: list[str] = field(default_factory=lambda: ["ruff"])
    ty_command: list[str] = field(default_factory=lambda: ["ty"])
    sage_command: list[str] = field(default_factory=lambda: ["sage"])
    shadow_dir_name: str = ".zsm-sagemath-lsp"
    log_level: str = "INFO"

    @classmethod
    def from_initialization_options(cls, options: dict[str, Any] | None) -> "ServerSettings":
        if not options:
            return cls()

        settings = cls()
        for key, value in options.items():
            if not hasattr(settings, key):
                continue
            setattr(settings, key, value)
        return settings

    def shadow_root(self, workspace_root: str | None) -> Path | None:
        if not workspace_root:
            return None
        return Path(workspace_root) / self.shadow_dir_name
