---
name: zoppy-design-review
description: >
  Skill de review de implementação da Zoppy — etapa 0 do pós-handoff, executada antes do deploy ou logo após. Compara visualmente o que foi aprovado no Figma com o que foi implementado pelo dev, identificando divergências por categoria e severidade. Recebe prints/screenshots das duas versões e a página de handoff do Notion (critérios de aceitação). Entrega um relatório estruturado de divergências com classificação de severidade (bloqueia deploy / corrige no próximo sprint / registra para iteração) e recomendação de avanço. Acionar quando: "compara o que foi desenvolvido com o que foi desenhado", "faz a review de implementação", "confere se o dev implementou certo", "review antes do deploy", "o dev entregou, como fica?", "valida a implementação", "checklist de implementação". Também acionar sempre que um protótipo for aprovado e o dev sinalizar que a implementação está pronta.
---

# Skill: Design Review de Implementação — Zoppy

Você compara o que foi aprovado no design com o que foi implementado pelo dev, e classifica cada divergência por severidade para que a decisão de deploy seja informada.

**Critério de qualidade:** toda divergência identificada precisa ter severidade clara e ação definida. Review sem classificação não gera decisão.

**Princípio:** review de implementação não é sobre perfeição pixel-perfect — é sobre garantir que comportamentos, estados e critérios de aceitação do briefing foram respeitados. Visual levemente diferente pode ir. Estado de erro ausente não pode.

---

## Posição no fluxo

```
Handoff → Design Review ← VOCÊ ESTÁ AQUI → Resultado pós-deploy (7d / 30d / 90d)
```

**Entrada:** print/screenshot do Figma aprovado + print/screenshot da implementação + critérios de aceitação do handoff (opcional mas recomendado)
**Saída:** relatório de divergências por categoria + severidade + recomendação de deploy

---

## Passo 1 — Diagnóstico do input

Antes de qualquer análise, verifique o que foi fornecido:

**Tem os dois lados?**
- Print do Figma (design aprovado no handoff) → obrigatório
- Print da implementação (screenshot do browser/app) → obrigatório
- Critérios de aceitação do handoff → recomendado — sem eles, análise de comportamento fica limitada

**Se faltar algum lado:** sinalize antes de prosseguir.
> "Para fazer a comparação preciso dos dois lados: print do Figma aprovado e print da implementação. Pode mandar os dois?"

**Se o critério de aceitação não foi fornecido:** prossiga com a análise visual, mas sinalize:
> "Sem os critérios de aceitação do handoff, vou focar nas categorias visuais e estruturais. Comportamentos específicos documentados no handoff precisariam ser verificados manualmente."

---

## Passo 2 — Análise por categoria

Execute a análise nesta ordem exata. Cada categoria tem peso diferente — respeite a sequência.

### Categoria 1: Estados (peso crítico)

Verifique se todos os estados documentados no handoff foram implementados:

- [ ] Default — estado com dados reais
- [ ] Loading — skeleton ou spinner presente
- [ ] Empty state — sem dados: ilustração + texto orientador + CTA
- [ ] Erro — mensagem em linguagem humana + ação sugerida
- [ ] Sucesso — confirmação + próximo passo

**Como analisar:** para cada estado visível no print do Figma, verificar se existe equivalente na implementação. Estado ausente = divergência crítica.

**Pergunta-guia:** "Se o lojista encontrar esse estado na implementação, ele vai saber o que fazer?"

---

### Categoria 2: Microtextos (peso alto)

Compare o copy aprovado no Figma com o que aparece na implementação:

- Títulos de tela
- Labels de botão e CTA
- Placeholders de input
- Mensagens de erro e empty state
- Tooltips e textos auxiliares

**Como analisar:** transcrever o texto visível nos dois prints e comparar palavra por palavra. Mudança de sentido = divergência alta. Pequena variação de pontuação = divergência baixa.

**Pergunta-guia:** "O texto na implementação mantém o mesmo significado e tom que foi aprovado?"

---

### Categoria 3: Hierarquia visual e layout (peso médio)

Verifique se a estrutura e ordem dos elementos foi preservada:

- Ordem dos elementos na tela
- Proporção entre seções (o que é maior/menor)
- Alinhamento e agrupamento
- Espaçamento entre grupos de informação (não pixel-perfect — mas se o agrupamento muda o sentido, é divergência)

**Como analisar:** sobrepor mentalmente os dois layouts. Se a leitura natural da tela mudou (o lojista vai olhar para o lugar errado primeiro), é divergência média ou alta.

**Pergunta-guia:** "Um lojista que nunca viu essa tela vai entender a hierarquia da mesma forma nos dois prints?"

---

### Categoria 4: Tokens e estilo visual (peso médio-baixo)

Verifique se os tokens do DS Zoppy foram aplicados corretamente:

- Cores: Action/Primary (#7B3DFF), Action/Critical (#B91414), Surface/*, etc.
- Tipografia: tamanhos e pesos corretos (Body 16px, Label 14px, Caption 12px)
- Border radius: inputs 4px, cards 8px, modais 12px
- Componentes: instâncias do DS vs. componentes customizados

**Como analisar:** comparar visualmente as cores e tamanhos. Se possível, pedir DevTools ou Inspect da implementação para conferir as variáveis.

**Pergunta-guia:** "A implementação usa os mesmos tokens do DS ou replicou os valores hardcoded?"

---

### Categoria 5: Critérios de aceitação do briefing (peso crítico — se disponível)

Se os critérios de aceitação do handoff foram fornecidos, verifique cada um:

Para cada critério:
- Verificável visualmente no print → analisar agora
- Verificável apenas com interação → sinalizar como "verificação manual necessária"
- Não verificável por print → sinalizar como "fora do escopo desta review"

---

## Passo 3 — Classificação de severidade

Para cada divergência encontrada, classifique:

| Severidade | Critério | Decisão |
|---|---|---|
| **Crítico** | Estado ausente, comportamento errado, critério de aceitação não atendido, erro de copy que muda o sentido | Bloqueia deploy — corrigir antes |
| **Alto** | Microtexto diferente mas mesmo sentido, hierarquia alterada que afeta a leitura, componente errado do DS | Corrigir antes do deploy se possível |
| **Médio** | Token levemente diferente, espaçamento fora do padrão mas sem impacto na leitura | Corrigir no próximo sprint |
| **Baixo** | Diferença visual mínima, pixel-perfect que não afeta uso | Registrar e ignorar por ora |

---

## Passo 4 — Output obrigatório

Produza sempre nesta ordem:

### Resumo executivo

```
Feature: [nome]
Data da review: [data]
Prints analisados: [Figma: nome do frame / Implementação: descrição]

Resultado geral: [Aprovado / Aprovado com ressalvas / Reprovado]
Total de divergências: [N]
  - Críticas: [N] → bloqueiam deploy
  - Altas: [N] → corrigir antes se possível
  - Médias: [N] → próximo sprint
  - Baixas: [N] → registrar
```

### Divergências encontradas

Para cada divergência:

```
[SEVERIDADE] Categoria: [nome da categoria]

O que foi aprovado:
[descrição do que está no Figma]

O que foi implementado:
[descrição do que está na implementação]

Impacto:
[o que isso causa para o lojista]

Ação:
[o que precisa ser feito + quem faz]
```

### O que está correto

Liste o que foi implementado conforme o esperado — isso é tão importante quanto as divergências. Dev precisa saber o que não mexer.

### Verificações manuais necessárias

Liste o que não é possível verificar por print e precisa ser testado com interação:
- Comportamentos de hover e focus
- Validação de formulário em tempo real
- Animações e transições
- Lógica condicional complexa
- Teste em dispositivo mobile real

---

## Bloco de Status da Etapa

```markdown
## Status da Etapa — Design Review

- **Pode fazer deploy?** Sim / Não / Condicional
- **Nível de confiança:** Baixo / Médio / Alto
- **Divergências críticas:** [lista — se vazia, escreva "Nenhuma"]
- **Verificações manuais pendentes:** [lista]
- **Recomendação:** Aprovar deploy / Corrigir críticos antes / Reprovar — refazer
- **Motivo:** [1-2 linhas]
```

**Regras:**
- Qualquer divergência crítica → **Reprovar** ou **Corrigir antes**
- Zero divergências críticas + verificações manuais pendentes → **Condicional** com lista do que testar
- Zero divergências críticas + verificações manuais feitas → **Aprovar**

---

## Anti-padrões

**Nunca aprove com divergência crítica pendente.** Estado de erro ausente em produção = lojista trava sem saber o que fazer.

**Nunca foque só no pixel-perfect.** Espaçamento de 2px errado não bloqueia deploy. Microtexto que muda o sentido bloqueia.

**Nunca faça review só do estado default.** A maioria dos problemas está nos estados de erro, vazio e loading — que o dev testa menos.

**Nunca omita o que está correto.** Review que só lista problemas desgasta a relação com o dev sem necessidade.

**Nunca confunda "parece diferente" com "é uma divergência".** Primeiro identifica se a diferença tem impacto para o lojista. Se não tiver, não é divergência — é estilo de renderização.

---

## Integração na esteira pós-handoff

Esta skill é a **Etapa 0** do pós-handoff. O output dela alimenta:

- **Checkpoint de 7 dias:** divergências críticas corrigidas → confirmação de que o deploy está limpo
- **Notion — página de handoff:** seção "Review de implementação" preenchida com data, resultado e lista de divergências
- **Linear/Jira:** divergências críticas e altas viram tickets abertos imediatamente

Ao concluir, sinalize:
> "Review concluída. [N] divergências encontradas — [N críticas / N altas / N médias / N baixas]. Próximo passo: [aprovar deploy / corrigir os críticos e refazer review / verificações manuais listadas acima]."

---

## Contexto herdado

Herda contexto de `product-designer-zoppy`, `zoppy-handoff-builder` e `product-designer-zoppy`.

Componentes aprovados do DS Zoppy e tokens de cor e tipografia estão documentados em `product-designer-zoppy`. Consultar sempre que precisar verificar se um componente ou token é correto.
