import ast
import re
import subprocess
import sys
from dataclasses import dataclass

MAX_LINES = 20
MAX_PARAMS = 4
MAX_DEPTH = 2
MAX_COMPLEXITY = 6
NESTING_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)
BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.comprehension)
SKIPPED_PREFIXES = ("migrations/",)
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True)
class Measure:
    path: str
    name: str
    line: int
    lines: int
    params: int
    depth: int
    complexity: int

    def violations(self) -> list[str]:
        checks = [
            (self.lines > MAX_LINES, f"linhas {self.lines}>{MAX_LINES}"),
            (self.params > MAX_PARAMS, f"parâmetros {self.params}>{MAX_PARAMS}"),
            (self.depth > MAX_DEPTH, f"aninhamento {self.depth}>{MAX_DEPTH}"),
            (self.complexity > MAX_COMPLEXITY, f"complexidade {self.complexity}>{MAX_COMPLEXITY}"),
        ]
        return [message for failed, message in checks if failed]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def changed_lines(base: str) -> dict[str, set[int]]:
    changed: dict[str, set[int]] = {}
    current = ""
    for row in git("diff", "-U0", f"{base}...HEAD", "--", "*.py").splitlines():
        if row.startswith("+++ "):
            path = row[6:] if row.startswith("+++ b/") else ""
            current = "" if path.startswith(SKIPPED_PREFIXES) else path
        hunk = HUNK.match(row)
        if hunk and current:
            start, count = int(hunk.group(1)), int(hunk.group(2) or "1")
            changed.setdefault(current, set()).update(range(start, start + count))
    return changed


def depth_of(node: ast.AST, level: int = 0) -> int:
    deepest = level
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        step = 1 if isinstance(child, NESTING_NODES) else 0
        deepest = max(deepest, depth_of(child, level + step))
    return deepest


def complexity_of(function: FunctionNode) -> int:
    branches = sum(isinstance(node, BRANCH_NODES) for node in ast.walk(function))
    bool_ops = sum(len(node.values) - 1 for node in ast.walk(function) if isinstance(node, ast.BoolOp))
    return 1 + branches + bool_ops


def params_of(function: FunctionNode) -> int:
    arguments = function.args
    names = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
    return len([name for name in names if name.arg not in ("self", "cls")])


def measure_file(path: str, touched: set[int]) -> list[Measure]:
    tree = ast.parse(open(path, encoding="utf-8").read())
    functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return [
        Measure(path, fn.name, fn.lineno, fn.end_lineno - fn.lineno + 1, params_of(fn), depth_of(fn), complexity_of(fn))
        for fn in functions
        if touched & set(range(fn.lineno, fn.end_lineno + 1))
    ]


def main(base: str) -> None:
    measures = [m for path, lines in changed_lines(base).items() for m in measure_file(path, lines)]
    for m in sorted(measures, key=lambda item: item.lines, reverse=True):
        verdict = "; ".join(m.violations()) or "ok"
        print(f"{m.path}:{m.line} {m.name} | linhas {m.lines} | params {m.params} | aninhamento {m.depth} | complexidade {m.complexity} | {verdict}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "origin/master")
