from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import tempfile

from .runtime import run_command


SAGE_QUERY_SCRIPT = r"""
import json
import sys
from sage.misc.dev_tools import import_statements
from sage.misc.sageinspect import sage_getdoc, sage_getdef, sage_getfile, sage_getsourcelines

name = sys.argv[1]
scope = {}
try:
    exec(import_statements(name, answer_as_str=True), scope)
    obj = scope[name]
    try:
        line = int(sage_getsourcelines(obj)[1])
    except Exception:
        line = 1
    print(json.dumps({
        "ok": True,
        "name": name,
        "signature": sage_getdef(obj, name),
        "doc": sage_getdoc(obj),
        "file": sage_getfile(obj),
        "line": line,
    }))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
"""

SAGE_MEMBER_SCRIPT = r"""
import json
import sys
from sage.misc.sageinspect import sage_getdoc, sage_getdef, sage_getfile, sage_getsourcelines
from sage.all import matrix, QQ, PolynomialRing, ZZ, EllipticCurve

kind = sys.argv[1]
member = sys.argv[2]

if kind == "matrix":
    obj = matrix(QQ, [[1]])
elif kind == "polynomial":
    R = PolynomialRing(ZZ, "x")
    obj = R.gen()
elif kind == "PolynomialRing":
    obj = PolynomialRing(ZZ, "x")
elif kind == "EllipticCurve":
    obj = EllipticCurve([0, 0, 1, -1, 0])
else:
    raise ValueError(f"unsupported kind: {kind}")

target = getattr(type(obj), member, None) or getattr(obj, member, None)
if target is None:
    raise AttributeError(member)

try:
    line = int(sage_getsourcelines(target)[1])
except Exception:
    line = 1

print(json.dumps({
    "ok": True,
    "name": member,
    "signature": sage_getdef(target, member),
    "doc": sage_getdoc(target),
    "file": sage_getfile(target),
    "line": line,
}))
"""


def _sage_env() -> dict[str, str]:
    home = Path(tempfile.gettempdir()) / "zsm-sagemath-lsp-sage-home"
    home.mkdir(parents=True, exist_ok=True)
    return {
        "HOME": str(home),
        "TERM": "dumb",
    }


@lru_cache(maxsize=512)
def query_symbol(sage_command: tuple[str, ...], symbol_name: str) -> dict | None:
    command = [*sage_command, "-python", "-c", SAGE_QUERY_SCRIPT, symbol_name]
    result = run_command(command, env=_sage_env(), timeout=25)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    data = json.loads(result.stdout)
    return data if data.get("ok") else None


@lru_cache(maxsize=512)
def query_member(sage_command: tuple[str, ...], kind: str, member: str) -> dict | None:
    command = [*sage_command, "-python", "-c", SAGE_MEMBER_SCRIPT, kind, member]
    result = run_command(command, env=_sage_env(), timeout=25)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    data = json.loads(result.stdout)
    return data if data.get("ok") else None
