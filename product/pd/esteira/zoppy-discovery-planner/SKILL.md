---
name: zoppy-discovery-planner
description: >
  Skill de Discovery da Zoppy — terceira etapa da esteira. Evidencia o problema com dados reais antes de qualquer solução visual. Herda toda a lógica de `zoppy-discovery` com bloco de Status da Etapa obrigatório e rastreamento explícito com o briefing. Acionar após briefing aprovado, ou quando houver problema de lojista sem solução definida, análise de comportamento, estruturação de pesquisa.
---

# Skill: Discovery Planner — Zoppy

> Esta skill é a **Fase 3** da esteira de produto da Zoppy.
> Herda toda a lógica e formato da `zoppy-discovery` com os seguintes acréscimos:
> - Referência explícita ao briefing aprovado
> - Bloco de Status da Etapa obrigatório ao final
> - Critério de confiança explícito antes de avançar para Ideação

Leia e execute `zoppy-discovery` como base. Os acréscimos abaixo se sobrepõem onde houver conflito.

---

## Posição no fluxo

```
PM Intake → Briefing → Discovery Planner ← VOCÊ ESTÁ AQUI → Ideação → DS Check → Prototipação → Handoff
```

**Entrada:** briefing aprovado (output de `zoppy-briefing-builder`)
**Saída:** problema central em evidências + hipóteses rankeadas + lacunas abertas + bloco de Status da Etapa

---

## Antes de executar o discovery

Verifique se o briefing foi aprovado:
- Há problema em uma frase?
- Há hipótese de solução?
- Há métricas definidas?

Se não — sinalize: *"Discovery sem briefing aprovado. Recomendo executar `zoppy-briefing-builder` primeiro para definir o problema antes de investigar evidências."*

**Rastreamento com o briefing:** ao iniciar o discovery, referencie explicitamente:
> "Discovery iniciado com base no briefing: [problema em uma frase do briefing]. A hipótese a investigar é: [hipótese do briefing]. O que precisa ser confirmado ou refutado: [lista das premissas do PM]."

---

## Execução

Execute o formato completo da `zoppy-discovery`:

1. Análise quantitativa (fontes disponíveis: HubSpot, Clarity, CS, Sales Bud)
2. Roteiro de entrevista qualitativa (quando necessário)
3. Benchmark competitivo e referências análogas
4. Síntese com hipóteses testáveis e HMWs

---

## Raciocínio explícito obrigatório

Antes do output, mostre:

> **Raciocínio:** [quais fontes estão disponíveis, o que o dado mostra vs. o que a hipótese do briefing assumia, contradições encontradas]

---

## Bloco de Status da Etapa — obrigatório

```markdown
## Status da Etapa — Discovery

- **Pode avançar?** [Sim / Não / Condicional]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi decidido:**
  - Problema central: [em evidências — não em opinião]
  - Hipóteses confirmadas do briefing: [lista]
  - Hipóteses refutadas: [lista — se houver, este é o dado mais importante]
- **Hipóteses que ainda precisam ser validadas:**
  - [o que o dado não respondeu — vai para ideação como restrição]
- **Lacunas abertas:**
  - [fontes que não estavam disponíveis e comprometem a certeza]
  - [perguntas que só entrevistas com lojistas reais responderiam]
- **Recomendação:** [Avançar / Revisar / Pausar]
- **Motivo:** [1-2 linhas]
```

**Critério para avançar para Ideação:**
- Problema central definido em evidências (não em opinião do PM ou da designer)
- Hipóteses rankeadas por impacto e facilidade de validação
- Lista explícita do que ainda não sabe — para não entrar na ideação com falsas certezas

Se nível de confiança for **Baixo**: recomendar **Pausar** e identificar o dado mínimo necessário para elevar para Médio antes de prototipar.

---

## Contexto herdado

Herda todo o contexto de `zoppy-discovery` e `product-designer-zoppy`.

**Ao concluir**, sinalize:
> "Discovery concluído. Nível de confiança: [X]. Próximo passo: `zoppy-ideation-designer` para explorar 3 variantes com base nas evidências — problema [resumo] com hipótese [resumo]."
