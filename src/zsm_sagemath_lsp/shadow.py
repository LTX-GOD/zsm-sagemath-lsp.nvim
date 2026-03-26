from __future__ import annotations

from dataclasses import dataclass
import ast
import keyword
import re
from typing import Iterable


RING_ASSIGN_RE = re.compile(
    r"^(?P<indent>\s*)(?P<ring>[A-Za-z_][A-Za-z0-9_]*)\s*\.<\s*(?P<gens>[A-Za-z_][A-Za-z0-9_\s,]*)\s*>\s*=\s*(?P<expr>.+?)\s*$"
)
FUNCTION_ASSIGN_RE = re.compile(
    r"^(?P<indent>\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)\((?P<args>[^()]*)\)\s*=\s*(?P<expr>.+?)\s*$"
)
ELLIPSIS_RANGE_RE = re.compile(r"(?P<left>[A-Za-z0-9_)\]]+)\s*\.\.\s*(?P<right>[A-Za-z0-9_(\[]+)")
SYMBOL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

PRELUDE_LINES = [
    "from typing import Any as __sage_any",
    "class __SagePlaceholder:",
    "    def gen(self, *args, **kwargs): return __SagePlaceholder()",
    "    def gens(self, *args, **kwargs): return tuple()",
    "    def factor(self, *args, **kwargs): return __SagePlaceholder()",
    "    def det(self, *args, **kwargs): return __SagePlaceholder()",
    "    def rank(self, *args, **kwargs): return __SagePlaceholder()",
    "    def nrows(self, *args, **kwargs): return 0",
    "    def ncols(self, *args, **kwargs): return 0",
    "    def inverse(self, *args, **kwargs): return __SagePlaceholder()",
    "    def transpose(self, *args, **kwargs): return __SagePlaceholder()",
    "    def roots(self, *args, **kwargs): return []",
    "    def degree(self, *args, **kwargs): return 0",
    "    def coefficients(self, *args, **kwargs): return []",
    "    def show(self, *args, **kwargs): return None",
    "    def latex(self, *args, **kwargs): return ''",
    "def sage_range(*args, **kwargs): return []",
    "def PolynomialRing(*args, **kwargs): return __SagePlaceholder()",
    "def LaurentPolynomialRing(*args, **kwargs): return __SagePlaceholder()",
    "def NumberField(*args, **kwargs): return __SagePlaceholder()",
    "def FiniteField(*args, **kwargs): return __SagePlaceholder()",
    "def matrix(*args, **kwargs): return __SagePlaceholder()",
    "def vector(*args, **kwargs): return __SagePlaceholder()",
    "def var(*args, **kwargs): return __SagePlaceholder()",
    "def EllipticCurve(*args, **kwargs): return __SagePlaceholder()",
    "ZZ = QQ = RR = CC = GF = SR = oo = infinity = Infinity = __SagePlaceholder()",
]

COMMON_METHODS = {
    "matrix": ["det", "rank", "nrows", "ncols", "inverse", "transpose", "charpoly", "eigenvalues"],
    "PolynomialRing": ["gen", "gens"],
    "polynomial": ["factor", "roots", "degree", "coefficients"],
    "EllipticCurve": ["rank", "gens", "order", "discriminant", "j_invariant"],
    "generic": ["show", "latex", "factor", "gens", "gen"],
}


@dataclass
class LocalSymbol:
    name: str
    kind: str
    line: int
    character: int
    origin: str = "local"


@dataclass
class ShadowDocument:
    source: str
    shadow_source: str
    line_map: list[int]
    local_symbols: list[LocalSymbol]
    inferred_types: dict[str, str]

    def original_position(self, shadow_line: int, shadow_character: int) -> tuple[int, int]:
        original_line = 0
        if 0 <= shadow_line < len(self.line_map) and self.line_map[shadow_line] >= 0:
            original_line = self.line_map[shadow_line]
        original_lines = self.source.splitlines() or [""]
        original_line = max(0, min(original_line, len(original_lines) - 1))
        original_char = min(shadow_character, len(original_lines[original_line]))
        return original_line, original_char


def build_shadow_document(source: str) -> ShadowDocument:
    shadow_lines: list[str] = []
    line_map: list[int] = []

    for prelude in PRELUDE_LINES:
        shadow_lines.append(prelude)
        line_map.append(-1)

    original_lines = source.splitlines()
    for line_number, line in enumerate(original_lines):
        transformed = transform_line(line)
        shadow_lines.extend(transformed)
        line_map.extend([line_number] * len(transformed))

    shadow_source = "\n".join(shadow_lines) + ("\n" if source.endswith("\n") or shadow_lines else "")
    local_symbols, inferred_types = collect_symbols(shadow_source, line_map)
    return ShadowDocument(
        source=source,
        shadow_source=shadow_source,
        line_map=line_map,
        local_symbols=local_symbols,
        inferred_types=inferred_types,
    )


def transform_line(line: str) -> list[str]:
    ring_match = RING_ASSIGN_RE.match(line)
    if ring_match:
        indent = ring_match.group("indent")
        ring_name = ring_match.group("ring")
        gens = [item.strip() for item in ring_match.group("gens").split(",") if item.strip()]
        expr = _rewrite_ranges(ring_match.group("expr"))
        if gens:
            tuple_repr = ", ".join(gens)
            if len(gens) == 1:
                tuple_repr += ","
            return [
                f"{indent}{ring_name} = {expr}",
                f"{indent}{tuple_repr} = {ring_name}.gens()",
            ]

    func_match = FUNCTION_ASSIGN_RE.match(line)
    if func_match:
        name = func_match.group("name")
        if name not in keyword.kwlist:
            indent = func_match.group("indent")
            args = func_match.group("args")
            expr = _rewrite_ranges(func_match.group("expr"))
            return [
                f"{indent}def {name}({args}):",
                f"{indent}    return {expr}",
            ]

    return [_rewrite_ranges(line)]


def _rewrite_ranges(line: str) -> str:
    return ELLIPSIS_RANGE_RE.sub(r"sage_range(\g<left>, \g<right>)", line)


def collect_symbols(shadow_source: str, line_map: list[int]) -> tuple[list[LocalSymbol], dict[str, str]]:
    symbols: list[LocalSymbol] = []
    inferred_types: dict[str, str] = {}
    try:
        tree = ast.parse(shadow_source)
    except SyntaxError:
        return symbols, inferred_types

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            line = _map_line(node.lineno - 1, line_map)
            symbols.append(LocalSymbol(node.name, "function", line, node.col_offset))
            for arg in node.args.args:
                symbols.append(LocalSymbol(arg.arg, "parameter", line, node.col_offset))
        elif isinstance(node, ast.ClassDef):
            line = _map_line(node.lineno - 1, line_map)
            symbols.append(LocalSymbol(node.name, "class", line, node.col_offset))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in _iter_targets(node):
                if isinstance(target, ast.Name):
                    line = _map_line(target.lineno - 1, line_map)
                    symbols.append(LocalSymbol(target.id, "variable", line, target.col_offset))
                    inferred = infer_assignment_type(node)
                    if inferred:
                        inferred_types[target.id] = inferred
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    line = _map_line(node.lineno - 1, line_map)
                    symbols.append(LocalSymbol(alias.asname, "import", line, node.col_offset))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                line = _map_line(node.lineno - 1, line_map)
                symbols.append(LocalSymbol(name, "import", line, node.col_offset))

    deduped: dict[tuple[str, str, int, int], LocalSymbol] = {}
    for symbol in symbols:
        deduped[(symbol.name, symbol.kind, symbol.line, symbol.character)] = symbol
    return sorted(deduped.values(), key=lambda item: (item.line, item.character, item.name)), inferred_types


def _map_line(shadow_line: int, line_map: list[int]) -> int:
    if 0 <= shadow_line < len(line_map) and line_map[shadow_line] >= 0:
        return line_map[shadow_line]
    return 0


def _iter_targets(node: ast.Assign | ast.AnnAssign) -> Iterable[ast.expr]:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            yield from _flatten_target(target)
    else:
        yield from _flatten_target(node.target)


def _flatten_target(target: ast.expr) -> Iterable[ast.expr]:
    if isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            yield from _flatten_target(element)
    else:
        yield target


def infer_assignment_type(node: ast.Assign | ast.AnnAssign) -> str | None:
    value = node.value if isinstance(node, ast.Assign) else node.value
    if isinstance(value, ast.Call):
        if isinstance(value.func, ast.Name):
            func_name = value.func.id
            if func_name in {"matrix", "PolynomialRing", "EllipticCurve"}:
                return func_name
        if isinstance(value.func, ast.Attribute) and value.func.attr == "gens":
            return "polynomial"
    return None


def find_word_at_position(source: str, line: int, character: int) -> str | None:
    lines = source.splitlines()
    if line < 0 or line >= len(lines):
        return None
    for match in SYMBOL_RE.finditer(lines[line]):
        if match.start() <= character <= match.end():
            return match.group()
    return None


def find_local_symbol(symbols: list[LocalSymbol], name: str) -> LocalSymbol | None:
    for symbol in symbols:
        if symbol.name == name:
            return symbol
    return None


def member_completions(base_name: str, inferred_types: dict[str, str]) -> list[str]:
    inferred = inferred_types.get(base_name)
    if inferred and inferred in COMMON_METHODS:
        return COMMON_METHODS[inferred]
    return COMMON_METHODS["generic"]
