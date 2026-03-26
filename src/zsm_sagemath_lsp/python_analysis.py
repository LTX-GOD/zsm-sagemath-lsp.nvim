from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import shutil
import sys

from .runtime import run_command

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


FROM_IMPORT_RE = re.compile(
    r"^\s*from\s+(?P<module>[A-Za-z_][A-Za-z0-9_\.]*)\s+import\s+(?P<prefix>[A-Za-z_][A-Za-z0-9_]*)?$"
)
IMPORT_COMPLETION_SCRIPT = r"""
import importlib
import json
import pkgutil
import sys

module_name = sys.argv[1]
mode = sys.argv[2]
prefix = sys.argv[3]
items = set()

module = importlib.import_module(module_name)

if mode == "member":
    items.update(getattr(module, "__all__", []))
    items.update(dir(module))
    if hasattr(module, "__path__"):
        for item in pkgutil.iter_modules(module.__path__):
            items.add(item.name)
else:
    if hasattr(module, "__path__"):
        for item in pkgutil.iter_modules(module.__path__):
            items.add(item.name)

results = sorted(name for name in items if not prefix or name.startswith(prefix))
print(json.dumps(results[:200]))
"""


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


def workspace_python_command(workspace_root: str | None) -> list[str]:
    if workspace_root:
        root = Path(workspace_root)
        if (root / "pyproject.toml").exists() and shutil.which("uv"):
            python_bin = root / ".venv" / "bin" / "python"
            python_exe = root / ".venv" / "Scripts" / "python.exe"
            if python_bin.exists() or python_exe.exists():
                return [workspace_python(workspace_root)]
            return ["uv", "run", "--project", workspace_root, "python"]
    return [workspace_python(workspace_root)]


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


def import_completions(line_prefix: str, workspace_root: str | None) -> list[PythonCompletion]:
    from_match = FROM_IMPORT_RE.match(line_prefix)
    if from_match:
        module_name = from_match.group("module")
        prefix = from_match.group("prefix") or ""
        return _run_import_completion(module_name, "member", prefix, workspace_root)

    stripped = line_prefix.lstrip()
    if stripped.startswith("import "):
        tail = stripped[len("import ") :].strip()
        if "." in tail:
            module_name, prefix = tail.rsplit(".", 1)
            return _run_import_completion(module_name, "submodule", prefix, workspace_root)

    return []


def _run_import_completion(
    module_name: str,
    mode: str,
    prefix: str,
    workspace_root: str | None,
) -> list[PythonCompletion]:
    command = [*workspace_python_command(workspace_root), "-c", IMPORT_COMPLETION_SCRIPT, module_name, mode, prefix]
    result = run_command(command, cwd=workspace_root, timeout=20)
    if result.returncode != 0 or not result.stdout.strip():
        return []

    try:
        names = json.loads(result.stdout)
    except Exception:
        return []

    return [
        PythonCompletion(
            label=name,
            kind="module" if mode == "submodule" else "statement",
            documentation=f"Imported from `{module_name}`",
        )
        for name in names
    ]
