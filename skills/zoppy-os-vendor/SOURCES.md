# Origens das skills oficiais

Consulta de licença e atualização: 2026-10-29. Cópias integrais, sem edição dos originais.

| Repositório | Commit | Data do commit | Licença | Skills copiadas |
| --- | --- | --- | --- | --- |
| [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills) | `126c384d8552dcb476b226c244172186cc3f4328` | 2026-10-26 | [MIT](licenses/langchain-ai_langchain-skills.LICENSE) | `deep-agents-core`, `deep-agents-memory`, `deep-agents-orchestration`, `langchain-dependencies`, `langchain-fundamentals`, `langchain-middleware`, `langgraph-persistence`, `langgraph-human-in-the-loop` |
| [honojs/skills](https://github.com/honojs/skills) | `e54ce51f6effaeb574ebd2629e89e086e14a2db3` | 2026-10-16 | [MIT](licenses/honojs_skills.LICENSE) | `hono` |
| [better-auth/skills](https://github.com/better-auth/skills) | `20c9e88a5c007461a703f1c213572b073196113e` | 2026-09-01 | Sem arquivo de licença; não redistribuído | Nenhuma |

## Better Auth: decisão de licença

O clone consultado não contém LICENSE/LICENCE/COPYING. Na verificação inicial de 2026-10-29,
`gh api repos/better-auth/skills` retornou `license: null` e
`gh api repos/better-auth/skills/license` retornou HTTP 404. A [árvore na web](https://github.com/better-auth/skills)
também não apresentava licença. Não se presume a licença da biblioteca para este repositório.
`better-auth/best-practices` e `security` ficam sem cópia; a skill própria
[os-official-docs](../zoppy-os/os-official-docs/SKILL.md) aponta para a instalação oficial e a documentação.
`organization-best-practices` permanece excluída: identidade, tenant, times e Master são da aplicação.

## Atualizar

Execute `bash skills/zoppy-os-vendor/update.sh` na raiz do repositório. Requer git, Python 3 e rede.
O script reclona as três origens, verifica as licenças, substitui somente as nove skills selecionadas
e suas licenças, atualiza esta proveniência e mostra o diff completo (inclusive arquivos novos).
Revalide com `quick_validate.py` e confira o diff antes de um commit. Não executa sync, push nem commit.

## Compatibilidade com o sync

`.github/workflows/sync-rules.yml` enumera `SOURCE/*/` e copia os arquivos de cada subpasta.
Assim, `licenses/` é copiada para `.claude/skills/licenses/` e aparece no marker, mas não vira skill:
não tem `SKILL.md` e o compilador Copilot a ignora. `SOURCES.md` e `update.sh` são ignorados.
O sync não valida frontmatter; uma falha de formato no validador não impede a cópia.
Não alterar os originais para adequá-los ao validador. Não houve alteração nem execução do sync.
