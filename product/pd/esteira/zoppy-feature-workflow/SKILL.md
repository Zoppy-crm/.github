---
name: zoppy-feature-workflow
description: "Skill de fluxo de trabalho por feature da Zoppy. Acionar quando a designer mencionar 'nova feature', 'nova demanda', 'começar uma feature', 'criar a pasta', 'organizar o arquivo', 'subir pra produção', 'atualizar o original', 'fluxo de design', 'onde salvar', 'como organizar'. Documenta a estrutura de pastas, arquivos, páginas e o ciclo completo desde a criação até a atualização das telas originais em produção."
---

# Skill: Fluxo de Trabalho por Feature — Zoppy

Esta skill documenta como cada feature da Zoppy deve ser organizada no Figma e qual é o ciclo completo de design — da pasta ao deploy.

---

## Estrutura de organização no Figma

```
Projeto Produto (figma.com/files/project/91435553)
├── 📁 [Nome da Feature]           ← uma pasta por feature
│   └── Feature — [Nome]           ← arquivo de design (duplicado do template)
├── 📁 Activation Date             ← exemplo já existente
│   └── Feature — Activation Date
└── (arquivo de telas originais — atualizado após aprovação)
```

**Regras:**
- Uma pasta por feature — nunca misturar features no mesmo arquivo
- Nome da pasta = nome exato da feature (sem prefixos, sem datas)
- O arquivo de design **sempre** parte do template

---

## Template base

**Arquivo:** `https://www.figma.com/design/zkbyeYgEfe6WAwx1Karfao`
**Como usar:** Duplicar o arquivo → mover para a pasta da feature → renomear para `Feature — [Nome]`

**Estrutura de páginas do template:**
```
🔒 Capa                    → dados da feature: nome, designer, PM, PRD, status, módulo, data
---
🔍 Panorama Geral          → telas afetadas, fluxo atual, componentes DS, restrições técnicas
📐 Wireframe               → mínimo 2 variantes de estrutura com trade-offs documentados
👁 Revisão                 → protótipo médio para validação PM + feedback registrado
🚧 WIP — [Nome da Feature] → prototipação final com tokens DS, anotações, fluxogramas, tabela de interações
---
✅ Final                   → frames aprovados movidos da WIP + links para Notion e ticket
```

---

## Ciclo completo de uma feature

### Fase 1 — Abertura
1. PM entrega o PRD no Notion
2. Criar pasta `[Nome da Feature]` dentro do projeto Produto no Figma
3. Duplicar o arquivo template e renomear para `Feature — [Nome]`
4. Mover o arquivo para dentro da pasta criada
5. Preencher a Capa: nome, designer, PM, link PRD, status="Em discovery", módulo

**Skill relevante:** `zoppy-discovery` (se ainda em discovery) ou `zoppy-briefing` (se PRD aprovado)

---

### Fase 2 — Briefing
1. Acionar `zoppy-briefing` com o PRD como insumo
2. Output: problema em 1 frase · hipótese · métricas com baseline · critérios de aceitação · restrições
3. Registrar o output na Capa do arquivo Figma
4. Atualizar status na Capa para "Em ideação"

---

### Fase 3 — Ideação (página 📐 Wireframe)
1. Acionar `zoppy-ideacao` com o briefing aprovado como insumo
2. Output: 3 variantes de solução com trade-offs + wireframes de baixa fidelidade no Figma
3. Avaliar trade-offs e escolher direção (ou híbrido entre variantes)
4. Registrar a variante escolhida com justificativa na página 📐 Wireframe

**Checklist antes de avançar:**
- [ ] 3 variantes geradas com trade-offs documentados
- [ ] Wireframes de baixa fidelidade criados no Figma
- [ ] Direção escolhida registrada com justificativa

---

### Fase 4 — Prototipação (página 🚧 WIP)
1. Renomear a página WIP para `🚧 WIP — [Nome da Feature]`
2. Acionar `zoppy-prototipacao` com o briefing aprovado
3. Output: spec de todos os estados, microtextos, edge cases, checklist
4. Executar no Figma via `zoppy-figma-mcp`:
   - Frames com tokens DS vinculados — nunca hardcodar cores
   - Instâncias reais do DS (não shapes manuais)
   - Frame `📋 Spec — [nome]` ao lado de cada frame
   - Fluxogramas de estado por cenário
   - Tabela de interações
   - Frame `📑 Índice — [Feature]` no topo com status de cada frame e pendências
5. Acionar `zoppy-documentacao` para gerar anotações e handoff no Notion

**Checklist antes de mover para Final:**
- [ ] Todos os frames têm anotação 📋 Spec ao lado
- [ ] Tokens DS — sem hardcode
- [ ] Fluxogramas criados
- [ ] Tabela de interações preenchida
- [ ] Pendências do índice resolvidas
- [ ] PM aprovou

---

### Fase 5 — Handoff (página ✅ Final)
1. Mover frames aprovados da WIP para Final (mover, não copiar)
2. Organizar por fluxo com labels
3. Colar link da documentação Notion
4. Colar link do ticket Linear
5. Atualizar status na Capa para "Pronto para dev"
6. Notificar o dev

---

### Fase 6 — Atualização das telas originais (pós-deploy)
**Quando:** após a feature subir para produção e ser validada

1. Abrir o arquivo de telas originais do produto (arquivo principal)
2. Localizar as telas afetadas mapeadas na página Panorama Geral
3. Substituir os frames originais pelos frames aprovados da página ✅ Final
4. Atualizar status na Capa do arquivo da feature para "Concluído"
5. Manter o arquivo da feature na pasta — serve como histórico de decisões

**Regra importante:** nunca editar as telas originais durante o desenvolvimento. Só atualizar depois do deploy.

---

## Status na Capa — valores válidos

| Status | Quando usar |
|---|---|
| Em discovery | Problema ainda não definido em evidências |
| Em briefing | PRD existe, briefing de design em andamento |
| Em ideação | Briefing fechado, explorando variantes de solução e wireframes |
| Em prototipação | Direção escolhida, spec e WIP em execução |
| Em revisão | Aguardando validação do PM |
| Pronto para dev | Frames na página Final, handoff gerado |
| Em dev | Dev implementando |
| Concluído | Deploy feito, telas originais atualizadas |
| Pausado | Feature suspensa — registrar motivo na Capa |
| Cancelado | Feature cancelada — manter arquivo como histórico |

---

## Arquivos-chave

| Arquivo | Uso | Link |
|---|---|---|
| Template de feature | Base para toda nova feature | `zkbyeYgEfe6WAwx1Karfao` |
| Produto (Activation Date) | Referência de feature completa | `q5wGKoXMI5JREpGSsa7dq4` |
| Design System (2024) | Fonte de componentes e tokens | `iCUju2TRogzUxwUaa9v8dt` |
| Projeto Produto | Pasta raiz no Figma | `figma.com/files/project/91435553` |

---

## Qual skill usar em cada fase

| Fase | Skill | Input esperado | Sinaliza próximo passo |
|---|---|---|---|
| Discovery / Research | `zoppy-discovery` | Descrição do problema ou dados do lojista | → `zoppy-briefing` |
| Briefing | `zoppy-briefing` | PRD do PM ou output do discovery | → `zoppy-ideacao` |
| Ideação + wireframe | `zoppy-ideacao` | Briefing aprovado | → `zoppy-prototipacao` |
| Spec de prototipação | `zoppy-prototipacao` | Direção escolhida na ideação | → `zoppy-figma-mcp` → `zoppy-documentacao` |
| Execução no Figma | `zoppy-figma-mcp` | Spec da prototipação | — |
| Documentação / handoff | `zoppy-documentacao` | Frames prontos na página WIP | → deploy |
| Contexto do produto | `product-designer-zoppy` | Qualquer dúvida sobre módulos, lojista, DS | — |

**Ordem de uso:**
```
product-designer-zoppy (sempre ativa como base)
          ↓
zoppy-discovery → zoppy-briefing → zoppy-ideacao → zoppy-prototipacao
                                                          ↓
                                               zoppy-figma-mcp (execução)
                                                          ↓
                                               zoppy-documentacao (handoff)
```

Cada skill sinaliza explicitamente o próximo passo ao concluir — não é necessário intervenção manual para saber o que acionar.

---

## Raciocínio em cadeia — ao iniciar qualquer demanda

Antes de executar qualquer coisa, perguntar internamente:

1. **Existe pasta da feature no projeto?** Se não → orientar criação manual + duplicar template
2. **Existe PRD?** Se não → acionar `zoppy-discovery` primeiro
3. **Briefing foi feito?** Se não → acionar `zoppy-briefing` antes de abrir o Figma
4. **Ideação foi feita?** Se não → acionar `zoppy-ideacao` antes de spec de prototipação
5. **Qual fase a feature está?** → Status na Capa define o que fazer agora
5. **É atualização pós-deploy?** → Ir para Fase 6 (não recriar frames, atualizar originais)

---

## Anti-padrões — nunca fazer

- ❌ Criar arquivo de feature sem pasta própria
- ❌ Trabalhar direto nas telas originais durante o desenvolvimento
- ❌ Copiar frames para Final em vez de mover
- ❌ Atualizar telas originais antes do deploy
- ❌ Começar wireframe sem PRD ou briefing aprovado
- ❌ Múltiplas features no mesmo arquivo
- ❌ Arquivo de feature sem link para o PRD na Capa

---

## Contexto herdado

Esta skill coordena todas as outras skills da Zoppy. Use `product-designer-zoppy` como base de contexto em qualquer situação. O arquivo de referência de feature completa é `q5wGKoXMI5JREpGSsa7dq4` (Activation Date).
