#!/usr/bin/env bash
set -euo pipefail

# Execute só para atualizar o vendor local; não faz commit, push nem sync.
vendor_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/zoppy-os-vendor.XXXXXXXX")"
trap 'rm -rf -- "$work_dir"' EXIT

git clone --depth 1 https://github.com/langchain-ai/langchain-skills.git "$work_dir/langchain"
git clone --depth 1 https://github.com/honojs/skills.git "$work_dir/hono"
git clone --depth 1 https://github.com/better-auth/skills.git "$work_dir/better-auth"

python3 - "$work_dir" "$vendor_dir" <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import subprocess
import sys

work, vendor = map(Path, sys.argv[1:])
selected = {
    "langchain": (
        "langchain-ai/langchain-skills", "config/skills",
        ["deep-agents-core", "deep-agents-memory", "deep-agents-orchestration",
         "langchain-dependencies", "langchain-fundamentals", "langchain-middleware",
         "langgraph-persistence", "langgraph-human-in-the-loop"],
    ),
    "hono": ("honojs/skills", "skills", ["hono"]),
}
stage, before = work / "stage", work / "before"
stage.mkdir()
before.mkdir()
(stage / "licenses").mkdir()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def skill_name(path):
    text = path.read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---", text, re.S)
    match = re.search(r"^name:\s*([^\n]+)", frontmatter[1], re.M) if frontmatter else None
    if not match:
        raise SystemExit(f"name ausente: {path}")
    return match[1].strip().strip("\"'")


seen = {}
for folder in ["shared", "react", "zoppy-os"]:
    for path in (vendor.parent / folder).glob("*/SKILL.md"):
        name = skill_name(path)
        if name in seen:
            raise SystemExit(f"Colisão de name: {seen[name]} e {path}")
        seen[name] = path

today = datetime.now(timezone.utc).date().isoformat()
lines = [
    "# Origens das skills oficiais", "",
    f"Consulta de licença e atualização: {today}. Cópias integrais, sem edição dos originais.", "",
    "| Repositório | Commit | Data do commit | Licença | Skills copiadas |",
    "| --- | --- | --- | --- | --- |",
]
for key, (origin, prefix, names) in selected.items():
    repo = work / key
    license_path = repo / "LICENSE"
    if not license_path.is_file() or not license_path.read_text().startswith("MIT License"):
        raise SystemExit(f"Licença de {origin} mudou; revisar antes de copiar.")
    license_name = origin.replace("/", "_") + ".LICENSE"
    shutil.copy2(license_path, stage / "licenses" / license_name)
    for name in names:
        source = repo / prefix / name
        actual = skill_name(source / "SKILL.md")
        if actual != name or actual in seen:
            raise SystemExit(f"name alterado ou em colisão: {source} ({actual})")
        seen[actual] = source
        shutil.copytree(source, stage / name, symlinks=True)
    commit, date = git(repo, "show", "-s", "--format=%H %cs").split()
    skills = ", ".join(f"`{name}`" for name in names)
    lines.append(f"| [{origin}](https://github.com/{origin}) | `{commit}` | {date} | "
                 f"[MIT](licenses/{license_name}) | {skills} |")

# A ausência de licença não autoriza redistribuição. Não adicionar cópia automaticamente.
auth = work / "better-auth"
auth_licenses = [p for p in auth.rglob("*") if p.is_file() and ".git" not in p.parts
                 and p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING"))]
if auth_licenses:
    raise SystemExit("Better Auth passou a ter arquivo de licença; revisar a decisão em SOURCES.md antes de atualizar.")
commit, date = git(auth, "show", "-s", "--format=%H %cs").split()
lines.extend([
    f"| [better-auth/skills](https://github.com/better-auth/skills) | `{commit}` | {date} | "
    "Sem arquivo de licença; não redistribuído | Nenhuma |", "",
    "## Better Auth: decisão de licença", "",
    "O clone consultado não contém LICENSE/LICENCE/COPYING. Na verificação inicial de 2026-10-29,",
    "`gh api repos/better-auth/skills` retornou `license: null` e",
    "`gh api repos/better-auth/skills/license` retornou HTTP 404. A [árvore na web](https://github.com/better-auth/skills)",
    "também não apresentava licença. Não se presume a licença da biblioteca para este repositório.",
    "`better-auth/best-practices` e `security` ficam sem cópia; a skill própria",
    "[os-official-docs](../zoppy-os/os-official-docs/SKILL.md) aponta para a instalação oficial e a documentação.",
    "`organization-best-practices` permanece excluída: identidade, tenant, times e Master são da aplicação.", "",
    "## Atualizar", "",
    "Execute `bash skills/zoppy-os-vendor/update.sh` na raiz do repositório. Requer git, Python 3 e rede.",
    "O script reclona as três origens, verifica as licenças, substitui somente as nove skills selecionadas",
    "e suas licenças, atualiza esta proveniência e mostra o diff completo (inclusive arquivos novos).",
    "Revalide com `quick_validate.py` e confira o diff antes de um commit. Não executa sync, push nem commit.", "",
    "## Compatibilidade com o sync", "",
    "`.github/workflows/sync-rules.yml` enumera `SOURCE/*/` e copia os arquivos de cada subpasta.",
    "Assim, `licenses/` é copiada para `.claude/skills/licenses/` e aparece no marker, mas não vira skill:",
    "não tem `SKILL.md` e o compilador Copilot a ignora. `SOURCES.md` e `update.sh` são ignorados.",
    "O sync não valida frontmatter; uma falha de formato no validador não impede a cópia.",
    "Não alterar os originais para adequá-los ao validador. Não houve alteração nem execução do sync.", "",
])
(stage / "SOURCES.md").write_text("\n".join(lines))

# Retire as árvores antigas para o temporário antes de copiar; não apague fora dele.
for source in sorted(stage.iterdir()):
    target = vendor / source.name
    if target.exists() or target.is_symlink():
        shutil.move(str(target), before / source.name)
    if source.is_dir():
        shutil.copytree(source, target, symlinks=True)
    else:
        shutil.copy2(source, target)

result = subprocess.run(["git", "diff", "--no-index", "--", str(before), str(stage)])
if result.returncode > 1:
    raise SystemExit(result.returncode)
print("Vendor atualizado localmente; revise as alterações antes de commitar.")
PY
