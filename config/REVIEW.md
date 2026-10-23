# Instruções de revisão — Zoppy

> Gerado a partir de `Zoppy-crm/.github` (`config/REVIEW.md`) pela action Sync Skills. Não edite aqui.

Este repositório já decidiu como o código deve ser. As decisões estão nas skills em `.claude/skills/`,
sincronizadas do repo `Zoppy-crm/.github`. Revise **contra essas decisões**, não contra boas práticas
genéricas.

## Antes de revisar, leia as skills

1. Leia `.claude/skills/pr-review/SKILL.md`. A seção **Invariantes** é a lista do que procurar neste
   repositório. Ignore as seções sobre como comentar (`gh pr comment`, comentário único, formato do
   comentário): aqui os achados saem no formato padrão do Code Review.
2. Leia as skills que o `pr-review` manda carregar para a área tocada pelo diff (por exemplo
   `code-review`, `code-conventions`, `domain`, `migration`, `angular-component`). Todas estão em
   `.claude/skills/<nome>/SKILL.md`. Regra objetiva de skill que o diff viola é achado, mesmo quando o
   código funciona.
3. A parte de critérios de aceite do `pr-review` depende da issue. Use só o que estiver no body do PR;
   não tente abrir issues.

## O que é Important

Reserve 🔴 Important para:

- dinheiro (cobrança, preço, cupom, limite, retry que cobra ou envia duas vezes);
- dado pessoal ou segredo em log, resposta de API ou erro;
- query sem filtro de empresa (multi-tenant) ou endpoint sem o guard que os vizinhos têm;
- migration que não é aditiva ou que edita migration já aplicada;
- código que contradiz uma decisão escrita no body do PR, no `CLAUDE.md` ou numa skill;
- bug que quebra comportamento em produção.

Violação de convenção, camada ou clean code das skills entra como 🟡 Nit, com o nome da skill e da
regra no comentário.

## Não reporte

- O que lint, formatação, tipagem e o workflow `pr-standards` já pegam.
- Arquivos em `.claude/`, `.github/copilot-instructions.md`, lockfiles e código gerado.
- Algo que o body do PR diz que ficou para outra entrega, de propósito.
