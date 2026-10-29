# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## Fronteiras

A árvore, os seis assuntos e a matriz de imports vêm dos dois documentos de arquitetura.
Os rascunhos `docs/proposals/skills/*/SKILL.md` contribuíram com separação de autoridade,
privacidade, erro de borda e efeitos. A transição de runtime dos rascunhos foi descartada:
o backend é somente Bun/TypeScript.

A skill define organização de código, não implantação, algoritmo financeiro, política de agenda,
delegação, retenção ou destino de telemetria. Os nomes finais de roles também não são fixados.
