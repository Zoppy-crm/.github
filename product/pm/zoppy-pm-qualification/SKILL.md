---
name: zoppy-pm-qualification
description: >
  Skill de Qualificação de Sinais de Produto da Zoppy — Fase 2 da esteira de PM. Recebe sinais estruturados da Fase 1 e decide o que avança para discovery, o que fica em observação e o que é descartado. Aplica as três perguntas obrigatórias de qualificação calibradas pela métrica norte de retenção. Só o PM qualifica — nunca o time de captura.

  Acionar após a Fase 1 (Captura) estar completa. Também acionar na triagem semanal de issues acumulados, quando o PM precisar revisar itens em observação, ou quando um item em observação atingir o prazo de 4 semanas.

  Qualificação é o filtro mais crítico do processo. Um item que passa sem evidência suficiente desperdiça discovery, priorização e design. Um item descartado por engano volta com mais contexto — não é irreversível.
---

# Qualificação de Sinais de Produto — Zoppy

Você transforma sinais estruturados em decisões claras. Cada item sai da qualificação com um de três status: **Descartado**, **Em observação**, ou **Qualificado para discovery**. Sem meio-termo, sem "talvez", sem item que fica em limbo.

**Princípio central:** sinal não é problema. Problema é sinal com evidência suficiente para justificar investimento de discovery.

---

## Métrica de fundo

A qualificação é calibrada pela métrica norte: **retenção — lojista ativo após 90 dias.**

A pergunta de fundo em toda qualificação é: *se esse problema fosse resolvido, isso aumentaria a probabilidade do lojista continuar ativo após 90 dias?*

Itens sem relação com a árvore de retenção precisam de justificativa muito forte para avançar.

```
RETENÇÃO 90 DIAS
        ↓
ATIVAÇÃO → ENGAJAMENTO → EXPANSÃO → SATISFAÇÃO
```

---

## As três perguntas obrigatórias

Todo item passa pelas três perguntas na ordem. A ordem importa.

---

### Pergunta 1 — Recorrência
**"Esse problema apareceu em mais de uma fonte ou mais de uma vez?"**

| Resposta | Significado |
|---|---|
| Sim — múltiplas fontes | Evidência forte. Avança para P2. |
| Sim — mesma fonte, múltiplas vezes | Evidência média. Avança para P2 com confiança média. |
| Não — ocorrência única | Vai para **Em observação**. Aguarda mais evidência. |

**Exceção:** ocorrência única com impacto crítico em ativação (bloqueia o lojista de chegar ao aha moment) pode avançar para P2 com confiança baixa documentada.

---

### Pergunta 2 — Impacto
**"Esse problema tem impacto mensurável em ativação, retenção ou expansão?"**

| Resposta | Significado |
|---|---|
| Sim — bloqueia ativação ou causa churn | Impacto alto. Avança para P3. |
| Sim — gera atrito recorrente | Impacto médio. Avança para P3. |
| Talvez — precisa de dado para confirmar | Impacto indefinido. Vai para **Em observação** até ter dado. |
| Não — melhoria cosmética sem impacto direto | Vai para **Descartado** ou backlog de melhorias futuras. |

---

### Pergunta 3 — Alinhamento estratégico
**"Está alinhado com os objetivos do trimestre?"**

| Resposta | Significado |
|---|---|
| Sim — resolve problema no caminho da retenção | Avança para **Qualificado para discovery**. |
| Parcialmente — relacionado mas não prioritário agora | Vai para **Em observação** com prazo de revisão. |
| Não — fora do foco atual | Vai para **Descartado** com justificativa registrada. |

---

## Os três status de saída

### ✅ Qualificado para discovery
O item respondeu sim nas três perguntas. Tem recorrência, tem impacto em retenção, está alinhado com os objetivos do trimestre. Vai para a Fase 3.

**Critério mínimo:** pelo menos duas fontes de evidência OU uma fonte com dado quantitativo confirmado.

---

### 👁️ Em observação
O item tem potencial mas ainda não tem evidência suficiente para justificar investimento de discovery. Fica monitorado.

**Regras de observação:**
- Prazo máximo: 4 semanas
- Se acumular nova evidência dentro do prazo → reavalia e pode qualificar
- Se não acumular evidência em 4 semanas → descartado automaticamente
- O PM revisa itens em observação na triagem semanal

---

### ❌ Descartado
O item não tem evidência suficiente, não tem impacto em retenção, ou está fora do foco atual. Não entra no backlog ativo.

**Regra importante:** descarte não é permanente. Se o mesmo problema aparecer novamente com mais evidência, volta para a Fase 1 com contexto acumulado — não começa do zero.

**Sempre registre o motivo do descarte.** Um descarte sem justificativa não tem valor — o motivo é o que permite requalificar no futuro com mais inteligência.

---

## Qualificação em lote — triagem semanal

Quando o PM faz a triagem semanal de issues acumulados:

1. **Liste todos os itens** que chegaram desde a última triagem
2. **Aplique as três perguntas** em cada item — rápido, sem aprofundar
3. **Agrupe itens similares** — sinais diferentes sobre o mesmo problema viram um único item com múltiplas evidências
4. **Classifique cada um** com o status de saída
5. **Apresente o resumo** ao PM: quantos qualificados, em observação e descartados
6. **Peça confirmação** antes de avançar os qualificados para discovery

Tempo esperado para triagem semanal: **30 minutos no máximo.** Se estiver tomando mais, os itens não estão chegando estruturados — problema na Fase 1.

---

## Agrupamento de sinais

Sinais diferentes sobre o mesmo problema devem ser agrupados em um único item antes da qualificação. O agrupamento aumenta a confiança e evita discovery duplicado.

**Critério de agrupamento:** mesmo módulo + mesmo comportamento do lojista + mesma barreira.

Exemplo:
- Sinal A: "lojista não encontra relatório de cashback" (CS)
- Sinal B: "lojista pergunta como ver resgates" (CS)
- Sinal C: dado do Clarity mostrando abandono na tela de relatórios

→ Um único item: "Lojista não encontra informações de resgate no módulo Giftback" com três evidências.

---

## Qualificação por categoria

### MELHORIA
A qualificação é mais direta — o problema já está acontecendo, tem sinal real.
- Foco nas perguntas 1 e 2: frequência e impacto são os critérios principais
- Pergunta 3 é filtro de timing — o problema pode ser real mas não prioritário agora

### FEATURE
A qualificação é mais criteriosa — ainda não tem evidência de uso, só hipótese.
- Pergunta 1 é mais difícil de responder — "múltiplas fontes" para feature significa múltiplos clientes com o mesmo objetivo, benchmark confirmando, ou dado de mercado
- Pergunta 2 exige raciocínio: *se construirmos isso, como move retenção?*
- Confiança inicial de FEATURE é sempre menor — precisa de discovery mais robusto

---

## Formato do item qualificado

Ao qualificar um item, produza o registro completo:

```markdown
## Item Qualificado

**Data de qualificação:** [data]
**Qualificado por:** PM
**Origem:** [referência ao sinal capturado na Fase 1]
**Categoria:** MELHORIA / FEATURE

---

**Módulo:** [módulo afetado]

**Problema central:**
[Uma frase clara descrevendo o problema — não a solução]

**Evidências:**
- [Fonte 1 — tipo, data, descrição]
- [Fonte 2 — tipo, data, descrição]
- [...]

**Recorrência:** Única / Recorrente / Alta frequência
**Impacto em retenção:** Alto / Médio / Baixo
**Alinhamento estratégico:** Alinhado / Parcial / Fora do foco

**Confiança total:** Baixo / Médio / Alto
**Status:** Qualificado para discovery

**Próximo passo:** Fase 3 — Discovery
```

---

## Formato do item descartado

```markdown
## Item Descartado

**Data:** [data]
**Origem:** [referência ao sinal]
**Categoria:** MELHORIA / FEATURE

**Motivo do descarte:**
[ ] Ocorrência única sem evidência adicional
[ ] Sem impacto mensurável em retenção
[ ] Fora do foco do trimestre
[ ] Duplicata de item existente
[ ] Fora do escopo do produto

**Justificativa:** [1-2 linhas explicando a decisão]

**Condição para requalificar:** [o que precisaria acontecer para esse item voltar]
```

---

## Bloco de Status da Fase — formato obrigatório

```markdown
## Status da Fase — Qualificação

- **Pode avançar?** Sim / Não / Condicional
- **Categoria do item:** MELHORIA / FEATURE
- **Impacto estimado em retenção:** Alto / Médio / Baixo / Indefinido
- **Nível de confiança:** Baixo / Médio / Alto
- **Resultado da qualificação:**
  - Qualificados para discovery: [lista]
  - Em observação: [lista com prazo]
  - Descartados: [lista com motivo]
- **Lacunas abertas:**
  - [o que ainda não sabemos e que o discovery precisa responder]
- **Recomendação:** Avançar para Discovery / Revisar / Aguardar evidência
- **Motivo:** [1-2 linhas]

---
➡️ Próxima fase: Discovery (zoppy-pm-discovery)
🙋 PM, confirma que podemos avançar para discovery?
```

---

## Regras de comportamento

**Só o PM qualifica.** Qualquer pessoa captura — só o PM decide o que avança. Nunca qualifique um item sem confirmação explícita do PM.

**Três perguntas na ordem.** Não pule perguntas. Não inverta. A ordem existe porque recorrência filtra antes de impacto, e impacto filtra antes de alinhamento.

**Descarte com justificativa sempre.** Um item descartado sem motivo registrado é inteligência perdida.

**Prazo de observação é inegociável.** 4 semanas sem nova evidência → descarte automático. O PM precisa ser avisado na triagem da semana 4.

**Pressão externa não qualifica item.** CEO pediu, Sales insistiu, parceiro solicitou — não são critérios de qualificação. Se o item não passa nas três perguntas, vai para observação ou descarte com o motivo documentado.

**Agrupe antes de qualificar.** Sinais sobre o mesmo problema viram um item com múltiplas evidências — não itens separados competindo no backlog.

**Confiança baixa não bloqueia, mas precisa ser honesta.** Um item pode avançar com confiança baixa desde que isso esteja documentado. O discovery vai compensar — mas o PM precisa saber que está fazendo uma aposta com menos evidência.
