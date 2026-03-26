from __future__ import annotations

from dataclasses import dataclass
import html
import json
import re
from importlib import resources


TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class SageSymbol:
    name: str
    kind: str
    doc: str


class SymbolIndex:
    def __init__(self) -> None:
        self._symbols: dict[str, SageSymbol] = {}
        self._load()

    def _load(self) -> None:
        data_path = resources.files("zsm_sagemath_lsp").joinpath("data/sagemath_symbols.json")
        data = json.loads(data_path.read_text(encoding="utf-8"))
        for kind in ("classes", "functions", "constants"):
            for item in data.get(kind, []):
                symbol = SageSymbol(
                    name=item["name"],
                    kind=kind[:-1] if kind.endswith("s") else kind,
                    doc=self._to_plain_text(item.get("doc", "")),
                )
                self._symbols[symbol.name] = symbol

    def _to_plain_text(self, raw: str) -> str:
        if not raw:
            return ""
        text = html.unescape(raw)
        text = TAG_RE.sub("", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def get(self, name: str) -> SageSymbol | None:
        return self._symbols.get(name)

    def complete(self, prefix: str, limit: int = 120) -> list[SageSymbol]:
        prefix_lower = prefix.lower()
        matches = [
            symbol
            for symbol in self._symbols.values()
            if not prefix or symbol.name.lower().startswith(prefix_lower)
        ]
        matches.sort(key=lambda item: item.name)
        return matches[:limit]
