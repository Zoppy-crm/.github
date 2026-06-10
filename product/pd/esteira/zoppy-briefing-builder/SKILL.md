---
name: zoppy-briefing-builder
description: >
  Skill de Briefing de Design da Zoppy — segunda etapa da esteira. Recebe o output do PM Intake e transforma em spec de design completa: problema em linguagem de lojista, hipótese falsificável, métricas com baseline, critérios de aceitação verificáveis e restrições. Produz o bloco de Status da Etapa ao final. Acionar após PM Intake concluído, ou quando houver PRD / demanda aprovada pronta para virar spec de design.
---

# Skill: Briefing Builder — Zoppy

> Esta skill é a **Fase 2** da esteira de produto da Zoppy.
> Herda toda a lógica e formato da `zoppy-briefing` com os seguintes acréscimos:
> - Referência explícita ao output do PM Intake
> - Bloco de Status da Etapa obrigatório ao final
> - Critério de confiança explícito antes de avançar para Discovery

Leia e execute `zoppy-briefing` como base. Os acréscimos abaixo se sobrepõem onde houver conflito.

---

## Posição no fluxo

```
PM Intake → Briefing Builder ← VOCÊ ESTÁ AQUI → Discovery → Ideação → DS Check → Prototipação → Handoff
```

**Entrada:** output do PM Intake (diagnóstico de qualidade, lacunas identificadas, perguntas para o PM)
**Saída:** briefing completo aprovado + bloco de Status da Etapa

---

## Antes de produzir o briefing

Verifique se o PM Intake foi executado:
- Há diagnóstico de qualidade do input?
- Há lista de lacunas identificadas?
- Há perguntas para o PM?

Se não houver PM Intake, sinalize: *"Briefing sem PM Intake executado antes. Recomendo executar `zoppy-pm-intake` primeiro para identificar lacunas antes de fechar o briefing."*

Se o PM Intake identificou lacunas críticas (classificação **Baixo**) ainda não respondidas pelo PM — sinalize antes de prosseguir: *"Há lacunas críticas do PM Intake ainda abertas. Avançar com o briefing agora significa construir sobre premissas não validadas. Recomendação: revisar com o PM antes."*

---

## Raciocínio explícito obrigatório

Antes do output, mostre:

> **Leitura do insumo:** [o que o PM Intake identificou como bom + o principal gap que o briefing precisa resolver]

---

## Output do briefing

Execute o formato completo da `zoppy-briefing`:

1. Problema em uma frase
2. Hipótese de solução
3. Métricas de sucesso (tabela)
4. Critérios de aceitação
5. Restrições e decisões já tomadas
6. Perguntas abertas

---

## Bloco de Status da Etapa — obrigatório

Ao final de cada briefing, produza:

```markdown
## Status da Etapa — Briefing

- **Pode avançar?** [Sim / Não / Condicional]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi decidido:**
  - Problema em uma frase: [colar aqui]
  - Hipótese de solução: [resumo em 1 linha]
  - Métricas definidas: [quantas, quais ferramentas]
- **Hipóteses que ainda precisam ser validadas:**
  - [lista — hipóteses do PM que o discovery vai confirmar ou refutar]
- **Lacunas abertas:**
  - [o que ainda não foi respondido pelo PM ou dev]
- **Recomendação:** [Avançar / Revisar / Pausar]
- **Motivo:** [1-2 linhas — por que pode ou não avançar para Discovery]
```

**Critério para avançar para Discovery:**
- Problema em uma frase aprovado pelo time
- Hipótese de solução falsificável (pode ser refutada pelos dados)
- Pelo menos 1 métrica com ferramenta de medição definida
- Critérios de aceitação com "medido por [como verificar]"

Se algum desses critérios falhar — **Revisar** antes de avançar.

---

## Contexto herdado

Herda todo o contexto de `zoppy-briefing` e `product-designer-zoppy`.

**Ao concluir**, sinalize:
> "Briefing fechado. Nível de confiança: [X]. Próximo passo: `zoppy-discovery-planner` para evidenciar o problema com dados reais antes de propor qualquer solução visual."
