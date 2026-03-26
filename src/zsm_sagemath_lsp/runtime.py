from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def executable_exists(command: list[str]) -> bool:
    if not command:
        return False
    return shutil.which(command[0]) is not None


def run_command(
    command: list[str],
    *,
    cwd: str | None = None,
    stdin_text: str | None = None,
    timeout: int = 20,
    env: dict[str, str] | None = None,
) -> CommandResult:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    proc = subprocess.run(
        command,
        input=stdin_text,
        text=True,
        capture_output=True,
        cwd=cwd,
        timeout=timeout,
        env=merged_env,
        check=False,
    )
    return CommandResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def write_shadow_file(
    shadow_root: Path | None,
    document_path: str | None,
    shadow_source: str,
    workspace_root: str | None = None,
) -> Path:
    if shadow_root is None:
        temp_dir = Path(tempfile.mkdtemp(prefix="zsm-sagemath-lsp-"))
        shadow_path = temp_dir / "buffer_shadow.py"
        shadow_path.write_text(shadow_source, encoding="utf-8")
        return shadow_path

    shadow_root.mkdir(parents=True, exist_ok=True)
    if document_path:
        doc_path = Path(document_path)
        if workspace_root:
            try:
                relative = doc_path.relative_to(Path(workspace_root))
            except ValueError:
                relative = Path(doc_path.name)
        else:
            relative = Path(doc_path.name)
        relative = relative.with_suffix(".shadow.py")
        shadow_path = shadow_root / relative
    else:
        shadow_path = shadow_root / "buffer_shadow.py"

    shadow_path.parent.mkdir(parents=True, exist_ok=True)
    shadow_path.write_text(shadow_source, encoding="utf-8")
    return shadow_path


def load_json(text: str) -> object:
    if not text.strip():
        return []
    return json.loads(text)
