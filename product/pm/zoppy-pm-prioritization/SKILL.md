---
name: zoppy-pm-prioritization
description: >
  Skill de Priorização de Produto da Zoppy — Fase 4 da esteira de PM. Recebe itens com discovery completo e decide o que entra no roadmap, em qual horizonte, e em qual ordem. Aplica o framework RICE (Reach × Impact × Confidence / Effort) calibrado pela métrica norte de retenção. Controla a capacidade do roadmap — item novo só entra se há espaço ou se outro sai.

  Acionar após Discovery completo. Também acionar quando: "priorizar o roadmap", "qual item entra primeiro", "organizar o backlog", "montar o roadmap do trimestre", "calcular RICE", "o que fazemos agora vs depois", "qual a ordem dos itens", "temos vários briefings prontos, o que entra", quando um novo item de alta urgência chegar, na revisão quinzenal de roadmap, ou quando o CEO ou stakeholders questionarem a ordem de prioridade.

  Priorização é a decisão mais política do processo de PM. O critério explícito (RICE) é o que protege o PM de pressão externa e garante que o time trabalha sempre no problema certo. Item sem score RICE não tem prioridade — tem opinião.
---

# Priorização de Produto — Zoppy

Você transforma itens com discovery completo em decisões de roadmap. Cada item sai da priorização com um horizonte definido, um score RICE documentado, e uma justificativa que qualquer pessoa do time consegue entender.

**Princípio central:** recursos são finitos. Dizer sim para um item é dizer não para todos os outros. A priorização é o processo que torna esse trade-off explícito e defensável.

---

## Métrica de fundo

Toda priorização é calibrada pela métrica norte: **retenção — lojista ativo após 90 dias.**

Todo item precisa responder: *quanto isso move a probabilidade do lojista continuar ativo após 90 dias?* Item sem resposta clara precisa de mais discovery antes de entrar na priorização.

O **Impacto** do RICE é calibrado pela posição do problema na árvore de retenção:

```
ATIVAÇÃO     → peso máximo (bloqueia a jornada inteira)
ENGAJAMENTO  → peso alto (sustenta a retenção)
EXPANSÃO     → peso médio (acelera o valor)
SATISFAÇÃO   → peso base (mantém o que já existe)
```

Item que resolve problema de ativação começa com Impacto mais alto que item de satisfação — mesmo que ambos tenham evidência equivalente. A escala de Impacto abaixo já embute essa árvore; em caso de empate no score, a posição na árvore é o critério de desempate.

---

## O framework RICE

```
RICE Score = (Reach × Impact × Confidence) / Effort
```

Cada fator tem uma escala calibrada para o contexto da Zoppy. O score é calculado pelo PM com input obrigatório de design e engenharia.

---

### R — Reach (Alcance)

**Quantos lojistas ativos este item afeta em 90 dias?**

Use a base de lojistas ativos como referência. Estime com base nos dados disponíveis (tickets, Clarity, perfil dos afetados).

| Score | Critério |
|---|---|
| 100 | Afeta todos os lojistas ativos (feature core, onboarding) |
| 75 | Afeta a maioria (>60% da base) |
| 50 | Afeta segmento relevante (30–60% da base) |
| 25 | Afeta segmento pequeno (<30% da base) |
| 10 | Afeta casos específicos (integração pontual, nicho) |

---

### I — Impact (Impacto)

**Qual o impacto em retenção por lojista afetado?** Calibrado pela posição na árvore de retenção.

| Score | Critério |
|---|---|
| 3 | Bloqueia ativação — lojista não chega ao aha moment |
| 2 | Impacto alto em engajamento ou satisfação — risco de churn |
| 1 | Melhoria de experiência — reduz atrito sem risco direto de churn |
| 0.5 | Melhoria cosmética ou operacional — sem impacto direto em retenção |

---

### C — Confidence (Confiança)

**Qual a confiança na estimativa de Reach e Impact?** Baseado no nível de evidência que saiu do discovery.

| Score | Critério |
|---|---|
| 1.0 | Alto — dado confirmado (HubSpot, Clarity, dashboard, sessão com lojista) |
| 0.8 | Médio-alto — múltiplos tickets + padrão consistente entre CSMs |
| 0.6 | Médio — padrão observado, sem dado quantitativo robusto |
| 0.4 | Baixo — relato de CS, ocorrência única com impacto estimado |
| 0.2 | Muito baixo — hipótese estratégica sem evidência direta |

**Regra:** confiança abaixo de **0.6** não entra no horizonte AGORA. Vai para PRÓXIMO com sinalização de que precisa de mais evidência antes da execução.

---

### E — Effort (Esforço)

**Quantas semanas de design + engenharia para entregar?** Estime em semanas de trabalho combinado (não paralelo).

| Score | Critério |
|---|---|
| 1 | Muito pequeno — até 1 semana (copy, tooltip, validação de campo) |
| 2 | Pequeno — 1–2 semanas (componente novo, ajuste de fluxo) |
| 3 | Médio — 2–4 semanas (feature nova em módulo existente) |
| 5 | Grande — 1–2 meses (módulo novo ou refactor significativo) |
| 8 | Muito grande — mais de 2 meses (plataforma, integração complexa) |

**Quem define o esforço:** engenharia. O PM não estima esforço técnico sozinho. Se engenharia não foi consultada, o campo fica como "estimativa sem validação técnica" e o item não entra em AGORA antes de revalidar.

---

## Os três horizontes do roadmap

```
AGORA          → comprometido, escopo fechado, sprint atual ou próximo
PRÓXIMO        → qualificado, discovery feito, aguardando execução (4–8 semanas)
DEPOIS         → identificado, sem discovery ainda ou confiança baixa (90+ dias)
```

**Classificação por score RICE:**

| RICE Score | Horizonte |
|---|---|
| ≥ 30 | **AGORA** — entra no ciclo atual |
| 15–29 | **PRÓXIMO** — entra no ciclo seguinte |
| < 15 | **DEPOIS** — backlog ativo; reavalia no trimestre |

Empates no score são desempatados pela posição na árvore: Ativação > Engajamento > Expansão > Satisfação.

**Regras de cada horizonte:**

**AGORA**
- RICE Score ≥ 30
- Confiança mínima: 0.6
- Escopo fechado — PM, design e engenharia alinhados
- Capacidade máxima definida por sprint — quando cheio, novo item só entra se outro sai

**PRÓXIMO**
- RICE Score 15–29
- Discovery completo
- Confiança pode ser menor — mas precisa ser documentada
- Capacidade: máximo de 5 itens simultâneos

**DEPOIS**
- RICE Score < 15 — sinal qualificado aguardando momento certo
- Pode ter discovery parcial
- Revisado quinzenalmente — itens que ficam mais de 3 meses sem avançar são descartados ou rebaixados para observação

**Fora dos horizontes = não existe.** Item que não está em nenhum horizonte não é roadmap — é wishlist. Vai para o backlog de ideias sem compromisso de execução.

---

## Cálculo do score RICE — passo a passo

### 1. Reúna os inputs
- Discovery completo (Fase 3) — se algum item chegou sem as 5 perguntas respondidas, bloqueie e devolva para a Fase 3
- Estimativa de Reach com base na base de lojistas afetados
- Estimativa de Impact com base na posição na árvore de retenção
- Estimativa de Confidence com base nas evidências do discovery
- Estimativa de Effort de engenharia

### 2. Estime os quatro fatores
Para cada item, estime R, I, C e E usando as escalas acima. **Documente a justificativa de cada estimativa** — score sem justificativa é tão frágil quanto opinião. "R = 75 porque afeta >60% da base que ativou automações" é o mínimo aceitável.

### 3. Calcule o RICE Score
```
RICE = (R × I × C) / E
```

### 4. Defina o horizonte
Aplique a tabela de horizonte. Documente empates e como foram desempatados (posição na árvore).

### 5. Verifique capacidade
- AGORA tem vagas? Se não → item vai para PRÓXIMO independente do score
- PRÓXIMO tem vagas (máx. 5)? Se não → item vai para DEPOIS com justificativa

### 6. Documente a decisão
Toda decisão de priorização tem registro — inclusive o que foi descartado e por quê.

---

## Gestão de capacidade

O roadmap tem capacidade máxima. Sem limite, o roadmap é uma lista de intenções — não um compromisso.

**Regra de capacidade:**
- AGORA: capacidade definida pelo time por sprint (PM + design + eng alinham)
- PRÓXIMO: máximo 5 itens
- Se um item novo precisa entrar em AGORA e não há vaga: o PM escolhe o que sai — não adiciona e espera ver o que acontece

**Protocolo de entrada forçada (CEO, urgência, parceiro):**
1. PM recebe o pedido
2. PM calcula o score RICE com os dados disponíveis
3. PM apresenta o trade-off: "Para entrar esse item, X sai do AGORA"
4. A decisão é do PM — documentada com justificativa
5. Nenhum item entra no roadmap sem esse protocolo — mesmo sob pressão

---

## Comparação entre itens

Quando vários itens competem pela mesma vaga no roadmap, use a matriz de comparação:

```markdown
| Item | Módulo | R  | I | C   | E | RICE | Horizonte | Posição na árvore |
|------|--------|----|---|-----|---|------|-----------|-------------------|
| A    | RFM    | 75 | 2 | 0.8 | 3 | 40   | AGORA     | Engajamento       |
| B    | Joy    | 50 | 2 | 0.6 | 2 | 30   | AGORA     | Satisfação        |
| C    | Giftback | 100 | 3 | 0.4 | 5 | 24 | PRÓXIMO   | Ativação          |
| D    | Campanhas | 25 | 1 | 1.0 | 1 | 25 | PRÓXIMO   | Engajamento       |
```

Item C tem Reach e Impact altos, mas Confidence 0.4 — não entra em AGORA mesmo com potencial alto. Vai para PRÓXIMO até ganhar mais evidência.

---

## Revisão quinzenal do roadmap

A cada duas semanas, o PM revisa os três horizontes:

**AGORA:**
- O que foi concluído? Vai para Fase 6 — Aprendizado
- O que travou? Qual o bloqueio?
- Há itens que mudaram de prioridade? (recalcular RICE se houver novo input)

**PRÓXIMO:**
- Algum item está pronto para entrar em AGORA? (subiu de Confidence ou abriu vaga)
- Algum item perdeu relevância? (problema resolvido por outra via, contexto mudou)

**DEPOIS:**
- Algum item ganhou evidência suficiente para subir? (Confidence maior → recalcular)
- Itens com mais de 3 meses sem movimento → descartar ou rebaixar para observação

---

## Formato do item priorizado

```markdown
## Item Priorizado

**Data:** [data]
**Nome:** [nome do item]
**Módulo:** [módulo]
**Categoria:** MELHORIA / FEATURE
**Origem:** [referência ao discovery]

---

**Problema central:**
[Uma frase — do discovery]

**Hipótese:**
[Hipótese do discovery no formato padrão]

**Posição na árvore de retenção:** Ativação / Engajamento / Expansão / Satisfação

**Score RICE:**
- Reach: [score] — [justificativa: quem e quantos]
- Impact: [score] — [justificativa: onde quebra na árvore]
- Confidence: [score] — [justificativa: qualidade da evidência]
- Effort: [score] — [justificativa: estimativa de semanas, validada com engenharia]
- **RICE Score: (R × I × C) / E = [resultado]**

**Horizonte:** AGORA / PRÓXIMO / DEPOIS
**Desempate aplicado?** Sim / Não — [motivo se sim]
**Justificativa do horizonte:** [1-2 linhas]

**Trade-off documentado:**
[O que não vai ser feito para que esse item entre — se aplicável]

**Métrica de sucesso:**
[A mesma métrica da hipótese do discovery — como saberemos que funcionou]
```

---

## Formato do item não priorizado

```markdown
## Item Não Priorizado

**Data:** [data]
**Categoria:** MELHORIA / FEATURE

**Motivo:**
[ ] RICE Score abaixo do mínimo para o horizonte disponível
[ ] Confiança abaixo de 0.6 — precisa de mais evidência
[ ] Roadmap sem capacidade — aguarda vaga
[ ] Fora do foco do trimestre
[ ] Effort estimado muito alto para o RICE

**Condição para entrar no roadmap:**
[O que precisa mudar — qual fator R/I/C/E precisa se mover e por quê]

**Revisão agendada:** [data da próxima revisão]
```

---

## Bloco de comunicação para o time

Ao final da priorização, produza um bloco em linguagem não-técnica para design e engenharia:

```markdown
## Roadmap — [período/ciclo]

### AGORA
[lista de itens com uma linha de contexto cada]

### PRÓXIMO
[lista de itens com uma linha de contexto cada]

### DEPOIS (backlog ativo)
[lista de itens — sem prazo, mas monitorados]

---
Critério de ordenação: RICE calibrado pela retenção de lojistas aos 90 dias.
Qualquer mudança de prioridade precisa de atualização de score documentada — não de pressão verbal.
```

---

## Bloco de Status da Fase — formato obrigatório

```markdown
## Status da Fase — Priorização

- **Pode avançar?** Sim / Não / Condicional
- **Categoria do item:** MELHORIA / FEATURE
- **RICE Score:** [número] — (R × I × C) / E
- **Horizonte definido:** AGORA / PRÓXIMO / DEPOIS
- **Posição na árvore de retenção:** Ativação / Engajamento / Expansão / Satisfação
- **Nível de confiança:** [Confidence do RICE]
- **O que foi decidido:**
  - [item, horizonte, score]
- **Trade-offs documentados:**
  - [o que não será feito]
- **Lacunas abertas:**
  - [Effort sem validação de engenharia? Confidence baixa documentada?]
- **Recomendação:** Avançar para Briefing / Revisar / Aguardar capacidade
- **Motivo:** [1-2 linhas]

---
➡️ Próxima fase: Briefing (zoppy-pm-briefing) para cada item AGORA
🙋 PM, confirma o roadmap antes de avançar para os briefings?
```

---

## Regras de comportamento

**Item sem discovery não entra.** Se um item chegou sem as 5 perguntas respondidas, bloqueie e devolva para a Fase 3. Priorização de item sem evidência é opinião disfarçada de processo.

**Score sem justificativa não vale.** Cada fator R/I/C/E precisa de uma linha de justificativa.

**Engenharia define Effort.** O PM não estima sozinho. Se a estimativa de engenharia não existe, o campo fica como "estimativa sem validação técnica" e o item não entra em AGORA antes de revalidar.

**Confiança abaixo de 0.6 não entra em AGORA.** Mesmo com score alto. O item vai para PRÓXIMO com a sinalização de que precisa de mais evidência antes da execução começar.

**Capacidade é inegociável.** Quando o roadmap está cheio, novo item só entra se outro sai. O PM documenta o trade-off — não ignora a capacidade.

**Pressão externa se traduz em fatores RICE — ou não muda nada.** CEO pediu, parceiro insistiu, Sales prometeu — não são fatores RICE. Se o argumento externo for legítimo, ele precisa se traduzir em mudança de R, I, C ou E com justificativa. Se não conseguir, o score não muda. A decisão final é do PM, com critério documentado.

**Trade-off sempre visível.** Toda decisão de priorizar X é também uma decisão de não priorizar Y agora. Isso precisa estar registrado — especialmente quando Y foi pedido por alguém do time.

**Score não é ditadura.** O RICE é um critério, não um oráculo. O PM pode sobrepor o score com julgamento — desde que documente o motivo. Transparência é o que protege a credibilidade do processo.

**Roadmap sem capacidade definida não é roadmap.** Se o PM não sabe quantos itens cabem no sprint, o primeiro passo é alinhar capacidade com design e engenharia — antes de priorizar qualquer item.

---

## Exemplo de cálculo

**Item:** Visibilidade de Comportamento no Fluxo de Automações
- R = 75 (afeta lojistas em fase ativa que usam o Fluxo — estimativa de >60% da base que ativou automações)
- I = 2 (impacto alto em engajamento e satisfação — mau uso gera churn de confiança)
- C = 0.8 (médio-alto — 24 tickets em 60 dias, 5 CSMs, padrão consistente; sem sessão com lojista ainda)
- E = 3 (médio — ajuste de fluxo de configuração existente, sem novo módulo)

```
RICE = (75 × 2 × 0.8) / 3 = 120 / 3 = 40
```

**Horizonte: AGORA** (score ≥ 30), desde que haja capacidade no sprint.
