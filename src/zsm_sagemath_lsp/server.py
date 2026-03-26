from __future__ import annotations

from dataclasses import dataclass
import ast
import logging
from pathlib import Path
import re
from typing import Iterable

from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument
from lsprotocol import types

from . import __version__
from .config import ServerSettings
from .runtime import executable_exists, load_json, run_command, write_shadow_file
from .shadow import (
    ShadowDocument,
    build_shadow_document,
    find_local_symbol,
    find_word_at_position,
    member_completions,
)
from .symbols import SymbolIndex


log = logging.getLogger(__name__)
WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class CompletionEntry:
    label: str
    kind: types.CompletionItemKind
    documentation: str = ""


class ZSMSageLanguageServer(LanguageServer):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.settings = ServerSettings()
        self.symbol_index = SymbolIndex()
        self.shadow_cache: dict[str, ShadowDocument] = {}

    def document_snapshot(self, doc: TextDocument) -> ShadowDocument:
        snapshot = self.shadow_cache.get(doc.uri)
        if snapshot and snapshot.source == doc.source:
            return snapshot
        snapshot = build_shadow_document(doc.source)
        self.shadow_cache[doc.uri] = snapshot
        return snapshot


server = ZSMSageLanguageServer("zsm-sagemath-lsp", __version__)


@server.feature(types.INITIALIZE)
def initialize(ls: ZSMSageLanguageServer, params: types.InitializeParams) -> None:
    ls.settings = ServerSettings.from_initialization_options(params.initialization_options)


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_open_or_change(
    ls: ZSMSageLanguageServer,
    params: types.DidOpenTextDocumentParams | types.DidChangeTextDocumentParams,
) -> None:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = collect_diagnostics(ls, doc)
    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=doc.uri,
            diagnostics=diagnostics,
            version=doc.version,
        )
    )


@server.feature(types.TEXT_DOCUMENT_COMPLETION)
def completion(
    ls: ZSMSageLanguageServer,
    params: types.CompletionParams,
) -> list[types.CompletionItem]:
    if not ls.settings.enable_completion:
        return []

    doc = ls.workspace.get_text_document(params.text_document.uri)
    snapshot = ls.document_snapshot(doc)
    line_text = doc.lines[params.position.line][: params.position.character]

    if line_text.endswith("."):
        base_name = _base_name_before_dot(line_text)
        labels = member_completions(base_name, snapshot.inferred_types) if base_name else []
        return [
            types.CompletionItem(label=label, kind=types.CompletionItemKind.Method)
            for label in labels[: ls.settings.max_completion_items]
        ]

    prefix_match = WORD_RE.search(line_text)
    prefix = prefix_match.group() if prefix_match else ""

    items: dict[str, CompletionEntry] = {}
    for symbol in snapshot.local_symbols:
        if prefix and not symbol.name.startswith(prefix):
            continue
        items[symbol.name] = CompletionEntry(
            label=symbol.name,
            kind=_completion_kind(symbol.kind),
            documentation=f"Local {symbol.kind}",
        )

    for symbol in ls.symbol_index.complete(prefix, limit=ls.settings.max_completion_items):
        items.setdefault(
            symbol.name,
            CompletionEntry(
                label=symbol.name,
                kind=_completion_kind(symbol.kind),
                documentation=symbol.doc[:1200],
            ),
        )

    results = list(items.values())
    results.sort(key=lambda item: item.label)
    return [
        types.CompletionItem(
            label=item.label,
            kind=item.kind,
            documentation=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value=item.documentation,
            )
            if item.documentation
            else None,
        )
        for item in results[: ls.settings.max_completion_items]
    ]


@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(ls: ZSMSageLanguageServer, params: types.HoverParams) -> types.Hover | None:
    if not ls.settings.enable_hover:
        return None

    doc = ls.workspace.get_text_document(params.text_document.uri)
    snapshot = ls.document_snapshot(doc)
    symbol_name = find_word_at_position(doc.source, params.position.line, params.position.character)
    if not symbol_name:
        return None

    local_symbol = find_local_symbol(snapshot.local_symbols, symbol_name)
    blocks: list[str] = []
    if local_symbol:
        blocks.append(f"```text\n{local_symbol.kind} {local_symbol.name}\n```")

    symbol = ls.symbol_index.get(symbol_name)
    if symbol:
        blocks.append(symbol.doc[:2000])

    if not blocks:
        return None

    start = params.position.character
    end = params.position.character
    line_text = doc.lines[params.position.line]
    for match in re.finditer(rf"\b{re.escape(symbol_name)}\b", line_text):
        if match.start() <= params.position.character <= match.end():
            start, end = match.start(), match.end()
            break

    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value="\n\n---\n\n".join(blocks),
        ),
        range=types.Range(
            start=types.Position(line=params.position.line, character=start),
            end=types.Position(line=params.position.line, character=end),
        ),
    )


@server.feature(types.TEXT_DOCUMENT_DEFINITION)
def definition(ls: ZSMSageLanguageServer, params: types.DefinitionParams) -> list[types.Location]:
    if not ls.settings.enable_definition:
        return []

    doc = ls.workspace.get_text_document(params.text_document.uri)
    snapshot = ls.document_snapshot(doc)
    symbol_name = find_word_at_position(doc.source, params.position.line, params.position.character)
    if not symbol_name:
        return []

    matches = [symbol for symbol in snapshot.local_symbols if symbol.name == symbol_name]
    return [
        types.Location(
            uri=doc.uri,
            range=types.Range(
                start=types.Position(line=symbol.line, character=symbol.character),
                end=types.Position(line=symbol.line, character=symbol.character + len(symbol.name)),
            ),
        )
        for symbol in matches
    ]


@server.feature(types.TEXT_DOCUMENT_REFERENCES)
def references(ls: ZSMSageLanguageServer, params: types.ReferenceParams) -> list[types.Location]:
    if not ls.settings.enable_references:
        return []

    doc = ls.workspace.get_text_document(params.text_document.uri)
    symbol_name = find_word_at_position(doc.source, params.position.line, params.position.character)
    if not symbol_name:
        return []

    locations: list[types.Location] = []
    for line_number, line in enumerate(doc.lines):
        for match in re.finditer(rf"\b{re.escape(symbol_name)}\b", line):
            locations.append(
                types.Location(
                    uri=doc.uri,
                    range=types.Range(
                        start=types.Position(line=line_number, character=match.start()),
                        end=types.Position(line=line_number, character=match.end()),
                    ),
                )
            )
    return locations


@server.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(
    ls: ZSMSageLanguageServer,
    params: types.DocumentSymbolParams,
) -> list[types.DocumentSymbol]:
    if not ls.settings.enable_document_symbols:
        return []
    doc = ls.workspace.get_text_document(params.text_document.uri)
    snapshot = ls.document_snapshot(doc)
    return [
        types.DocumentSymbol(
            name=symbol.name,
            kind=_document_symbol_kind(symbol.kind),
            range=types.Range(
                start=types.Position(line=symbol.line, character=symbol.character),
                end=types.Position(line=symbol.line, character=symbol.character + len(symbol.name)),
            ),
            selection_range=types.Range(
                start=types.Position(line=symbol.line, character=symbol.character),
                end=types.Position(line=symbol.line, character=symbol.character + len(symbol.name)),
            ),
        )
        for symbol in snapshot.local_symbols
        if symbol.kind in {"function", "class", "variable"}
    ]


def collect_diagnostics(ls: ZSMSageLanguageServer, doc: TextDocument) -> list[types.Diagnostic]:
    if not ls.settings.enable_diagnostics:
        return []

    snapshot = ls.document_snapshot(doc)
    diagnostics: list[types.Diagnostic] = []
    diagnostics.extend(_syntax_diagnostics(snapshot))
    diagnostics.extend(_ruff_diagnostics(ls, doc, snapshot))
    diagnostics.extend(_ty_diagnostics(ls, doc, snapshot))
    return diagnostics


def _syntax_diagnostics(snapshot: ShadowDocument) -> list[types.Diagnostic]:
    try:
        ast.parse(snapshot.shadow_source)
    except SyntaxError as exc:
        line, character = snapshot.original_position(max(exc.lineno - 1, 0), max((exc.offset or 1) - 1, 0))
        return [
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=line, character=character),
                    end=types.Position(line=line, character=character + 1),
                ),
                severity=types.DiagnosticSeverity.Error,
                source="zsm-sagemath-lsp",
                message=exc.msg,
            )
        ]
    return []


def _ruff_diagnostics(
    ls: ZSMSageLanguageServer,
    doc: TextDocument,
    snapshot: ShadowDocument,
) -> list[types.Diagnostic]:
    if not ls.settings.enable_ruff or not executable_exists(ls.settings.ruff_command):
        return []

    shadow_filename = _shadow_filename(doc)
    result = run_command(
        [
            *ls.settings.ruff_command,
            "check",
            "--output-format",
            "json",
            "--stdin-filename",
            shadow_filename,
            "-",
        ],
        cwd=ls.workspace.root_path,
        stdin_text=snapshot.shadow_source,
    )

    if result.returncode not in {0, 1}:
        log.warning("ruff failed: %s", result.stderr.strip())
        return []

    raw = load_json(result.stdout)
    diagnostics: list[types.Diagnostic] = []
    for item in raw if isinstance(raw, list) else []:
        location = item.get("location", {})
        end_location = item.get("end_location", location)
        start_line, start_char = snapshot.original_position(
            max(location.get("row", 1) - 1, 0),
            max(location.get("column", 1) - 1, 0),
        )
        end_line, end_char = snapshot.original_position(
            max(end_location.get("row", 1) - 1, 0),
            max(end_location.get("column", 1) - 1, 0),
        )
        diagnostics.append(
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=start_line, character=start_char),
                    end=types.Position(line=end_line, character=max(end_char, start_char + 1)),
                ),
                severity=types.DiagnosticSeverity.Warning,
                source="ruff",
                code=item.get("code"),
                message=item.get("message", "ruff diagnostic"),
            )
        )
    return diagnostics


def _ty_diagnostics(
    ls: ZSMSageLanguageServer,
    doc: TextDocument,
    snapshot: ShadowDocument,
) -> list[types.Diagnostic]:
    if not ls.settings.enable_ty or not executable_exists(ls.settings.ty_command):
        return []

    shadow_root = ls.settings.shadow_root(ls.workspace.root_path)
    shadow_path = write_shadow_file(
        shadow_root,
        doc.path,
        snapshot.shadow_source,
        ls.workspace.root_path,
    )
    command = [*ls.settings.ty_command, "check", "--output-format", "gitlab"]
    if ls.workspace.root_path:
        command.extend(["--project", ls.workspace.root_path])
    command.append(str(shadow_path))
    result = run_command(command, cwd=ls.workspace.root_path)

    if result.returncode not in {0, 1}:
        log.warning("ty failed: %s", result.stderr.strip())
        return []

    raw = load_json(result.stdout)
    diagnostics: list[types.Diagnostic] = []
    for item in raw if isinstance(raw, list) else []:
        begin = item.get("location", {}).get("positions", {}).get("begin", {})
        end = item.get("location", {}).get("positions", {}).get("end", begin)
        start_line, start_char = snapshot.original_position(
            max(begin.get("line", 1) - 1, 0),
            max(begin.get("column", 1) - 1, 0),
        )
        end_line, end_char = snapshot.original_position(
            max(end.get("line", 1) - 1, 0),
            max(end.get("column", 1) - 1, 0),
        )
        severity = item.get("severity", "major")
        diagnostics.append(
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=start_line, character=start_char),
                    end=types.Position(line=end_line, character=max(end_char, start_char + 1)),
                ),
                severity=_ty_severity(severity),
                source="ty",
                code=item.get("check_name"),
                message=item.get("description", "ty diagnostic"),
            )
        )
    return diagnostics


def _shadow_filename(doc: TextDocument) -> str:
    if doc.path:
        return f"{doc.path}.shadow.py"
    return "buffer.shadow.py"


def _base_name_before_dot(text: str) -> str | None:
    stripped = text[:-1]
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", stripped)
    return match.group(1) if match else None


def _completion_kind(kind: str) -> types.CompletionItemKind:
    mapping = {
        "function": types.CompletionItemKind.Function,
        "class": types.CompletionItemKind.Class,
        "variable": types.CompletionItemKind.Variable,
        "parameter": types.CompletionItemKind.Variable,
        "constant": types.CompletionItemKind.Constant,
        "import": types.CompletionItemKind.Module,
    }
    return mapping.get(kind, types.CompletionItemKind.Text)


def _document_symbol_kind(kind: str) -> types.SymbolKind:
    mapping = {
        "function": types.SymbolKind.Function,
        "class": types.SymbolKind.Class,
        "variable": types.SymbolKind.Variable,
    }
    return mapping.get(kind, types.SymbolKind.Object)


def _ty_severity(value: str) -> types.DiagnosticSeverity:
    if value in {"blocker", "critical", "major"}:
        return types.DiagnosticSeverity.Error
    if value in {"minor"}:
        return types.DiagnosticSeverity.Warning
    return types.DiagnosticSeverity.Information
