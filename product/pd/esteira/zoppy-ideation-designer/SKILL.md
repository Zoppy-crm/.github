---
name: zoppy-ideation-designer
description: >
  Skill de Ideação da Zoppy — quarta etapa da esteira. Gera 3 variantes genuinamente diferentes de solução, executa layouts no Figma com texto real e 2 estados, e apresenta trade-offs sem recomendar. Herda toda a lógica de `zoppy-ideacao` com bloco de Status da Etapa obrigatório e rastreamento explícito com o discovery. Acionar após discovery concluído. Nunca antes.
---

# Skill: Ideation Designer — Zoppy

> Esta skill é a **Fase 4** da esteira de produto da Zoppy.
> Herda toda a lógica e formato da `zoppy-ideacao` com os seguintes acréscimos:
> - Referência explícita ao discovery e briefing
> - Bloco de Status da Etapa obrigatório ao final
> - Critério de confiança antes de avançar para DS Check + Prototipação
> - Execução devagar no Figma: um estado por vez, verificado antes do próximo

Leia e execute `zoppy-ideacao` como base. Os acréscimos abaixo se sobrepõem onde houver conflito.

---

## Posição no fluxo

```
PM Intake → Briefing → Discovery → Ideation Designer ← VOCÊ ESTÁ AQUI → DS Check → Prototipação → Handoff
```

**Entrada:** discovery concluído + briefing aprovado
**Saída:** 3 variantes com trade-offs + layouts no Figma + direção escolhida + bloco de Status da Etapa

---

## Antes de gerar variantes

Verifique se o discovery foi concluído:
- Há problema central em evidências?
- Há hipóteses rankeadas?

Se não — sinalize: *"Ideação sem discovery concluído. Recomendo executar `zoppy-discovery-planner` primeiro. Gerar variantes antes do problema estar evidenciado é otimizar a solução errada."*

**Rastreamento com o discovery:** antes de gerar as variantes, referencie:
> "Leitura do briefing: [problema] · [superfície afetada] · [lojista em contexto] · [principal restrição do DS ou técnica]"

---

## Regra de execução devagar no Figma

Esta etapa executa layouts de ideação — não protótipos com DS. Mas mesmo em ideação, a regra é:

**Um frame por vez.** Antes de criar o segundo estado, verificar se o primeiro está correto — nome do frame, posição, texto real, hierarquia visual básica.

Nunca criar 6 frames de uma vez sem verificar o primeiro. Velocidade de execução no Figma é inversamente proporcional à qualidade do output.

---

## Execução

Execute o formato completo da `zoppy-ideacao`:

1. Leitura do briefing (explícita, antes das variantes)
2. 3 variantes com: estrutura, quando funciona melhor, trade-off
3. Layouts no Figma: página `💡 Ideação — [Nome da Feature]`, 2 estados por variante
4. Apresentação dos trade-offs sem recomendar
5. Aguardar direção escolhida pela designer

---

## Bloco de Status da Etapa — obrigatório

```markdown
## Status da Etapa — Ideação

- **Pode avançar?** [Sim / Não — aguardando direção / Condicional]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi decidido:**
  - Direção escolhida: [Variante A / B / C / Híbrido — ou "Aguardando escolha"]
  - Motivo da escolha (quando registrado pela designer): [resumo]
- **Hipóteses que ainda precisam ser validadas:**
  - [o que a variante escolhida assume que ainda não foi testado]
- **Lacunas abertas:**
  - [o que a ideação revelou que precisa ser resolvido antes de prototipar]
- **Recomendação:** [Avançar para DS Check / Aguardar direção / Revisar variantes]
- **Motivo:** [1-2 linhas]
```

**Critério para avançar para DS Check:**
- Direção escolhida (variante ou híbrido claramente definido)
- Trade-offs da escolha explicitamente registrados
- Nenhuma decisão estrutural em aberto que precise de mais ideação

**Critério para não avançar:**
- Designer ainda não escolheu direção
- As 3 variantes parecem a mesma solução com detalhes diferentes (rever divergência)
- A variante escolhida tem premissa técnica que precisa ser validada com eng antes de prototipar

---

## Contexto herdado

Herda todo o contexto de `zoppy-ideacao`, `product-designer-zoppy` e `zoppy-figma-mcp`.

**Ao concluir**, sinalize:
> "Ideação concluída. Nível de confiança: [X]. Direção: [variante escolhida]. Próximo passo: `zoppy-design-system-figma` para verificar componentes disponíveis antes de executar no Figma."
