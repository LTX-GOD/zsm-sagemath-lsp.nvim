from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import sys

try:
    import jedi
except ImportError:  # pragma: no cover - optional runtime dependency during static checks
    jedi = None


@dataclass
class PythonCompletion:
    label: str
    kind: str
    documentation: str


@dataclass
class PythonDefinition:
    path: str | None
    line: int
    character: int
    name: str


@dataclass
class PythonHover:
    value: str


def jedi_available() -> bool:
    return jedi is not None


def workspace_python(workspace_root: str | None) -> str:
    candidates: list[Path] = []
    if workspace_root:
        root = Path(workspace_root)
        candidates.extend(
            [
                root / ".venv" / "bin" / "python",
                root / ".venv" / "Scripts" / "python.exe",
            ]
        )

    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        candidates.extend(
            [
                Path(virtual_env) / "bin" / "python",
                Path(virtual_env) / "Scripts" / "python.exe",
            ]
        )

    candidates.append(Path(sys.executable))
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


@lru_cache(maxsize=16)
def _project(workspace_root: str | None, environment_path: str):
    if jedi is None:
        return None
    root = workspace_root or os.getcwd()
    try:
        return jedi.Project(path=root, environment_path=environment_path)
    except TypeError:
        return jedi.Project(path=root)


def _script(snapshot, workspace_root: str | None, doc_path: str | None, line: int, character: int):
    if jedi is None:
        return None, None, None

    symbol_name = snapshot.find_word(line, character)
    shadow_line, shadow_character = snapshot.shadow_position(line, character, symbol_name)
    environment_path = workspace_python(workspace_root)
    shadow_path = f"{doc_path}.shadow.py" if doc_path else "buffer.shadow.py"
    project = _project(workspace_root, environment_path)
    return (
        jedi.Script(code=snapshot.shadow_source, path=shadow_path, project=project),
        shadow_line,
        shadow_character,
    )


def completions(snapshot, workspace_root: str | None, doc_path: str | None, line: int, character: int) -> list[PythonCompletion]:
    script, shadow_line, shadow_character = _script(snapshot, workspace_root, doc_path, line, character)
    if script is None:
        return []

    try:
        results = script.complete(line=shadow_line + 1, column=shadow_character)
    except Exception:
        return []

    items: list[PythonCompletion] = []
    for item in results:
        signature_blocks = [f"```python\n{sig.to_string()}\n```" for sig in item.get_signatures()]
        docstring = item.docstring(raw=True)
        documentation = "\n\n---\n\n".join([block for block in ["\n\n".join(signature_blocks), docstring] if block])
        items.append(
            PythonCompletion(
                label=item.name,
                kind=item.type,
                documentation=documentation,
            )
        )
    return items


def hover(snapshot, workspace_root: str | None, doc_path: str | None, line: int, character: int) -> PythonHover | None:
    script, shadow_line, shadow_character = _script(snapshot, workspace_root, doc_path, line, character)
    if script is None:
        return None

    try:
        names = script.infer(line=shadow_line + 1, column=shadow_character) or script.goto(
            line=shadow_line + 1,
            column=shadow_character,
            follow_imports=True,
            follow_builtin_imports=True,
        )
    except Exception:
        return None

    blocks: list[str] = []
    for name in names:
        signatures = [f"```python\n{sig.to_string()}\n```" for sig in name.get_signatures()]
        docstring = name.docstring(raw=True)
        value = "\n\n---\n\n".join([block for block in ["\n\n".join(signatures), docstring] if block])
        if value:
            blocks.append(value)

    if not blocks:
        return None
    return PythonHover(value="\n\n---\n\n".join(blocks))


def definitions(snapshot, workspace_root: str | None, doc_path: str | None, line: int, character: int) -> list[PythonDefinition]:
    script, shadow_line, shadow_character = _script(snapshot, workspace_root, doc_path, line, character)
    if script is None:
        return []

    try:
        names = script.goto(
            line=shadow_line + 1,
            column=shadow_character,
            follow_imports=True,
            follow_builtin_imports=True,
        )
    except Exception:
        return []

    definitions_list: list[PythonDefinition] = []
    shadow_path = f"{doc_path}.shadow.py" if doc_path else "buffer.shadow.py"
    for name in names:
        module_path = str(name.module_path) if getattr(name, "module_path", None) else None
        if module_path == shadow_path:
            original_line, original_character = snapshot.original_position(
                max(name.line - 1, 0),
                max(name.column, 0),
            )
            definitions_list.append(
                PythonDefinition(
                    path=doc_path,
                    line=original_line,
                    character=original_character,
                    name=name.name,
                )
            )
        else:
            definitions_list.append(
                PythonDefinition(
                    path=module_path,
                    line=max((name.line or 1) - 1, 0),
                    character=max(name.column or 0, 0),
                    name=name.name,
                )
            )
    return definitions_list
