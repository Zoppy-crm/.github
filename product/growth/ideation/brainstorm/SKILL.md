---
name: zoppy-growth-brainstorm
description: >
  Skill de Brainstorm da Zoppy — Fase 2 da esteira de growth. Transforma inputs (dados, insights, pesquisas, métricas, problemas de funil) em outputs acionáveis: experimentos de growth estruturados, sínteses de pesquisa, hipóteses priorizadas ou planos de ação. Opera sempre em modo conversa — sense-making antes de divergir, divergência ancorada em ativos existentes, clustering antes de estruturar hipóteses, priorização por ICE.

  Acionar quando o Growth trouxer dado, insight ou research já processado e quiser discutir, explorar hipóteses ou gerar experimentos testáveis. Trigger on: "vamos discutir", "me ajuda a pensar", "o que podemos fazer com isso", "quais hipóteses", "como priorizamos", "brainstorm", "preciso de ideias", "o que isso indica", planejamento de roadmap, definição de OKR, síntese de pesquisa, análise de métrica, bottleneck de funil, problemas de retenção/ativação/engajamento.
---

# Brainstorm -> Growth Experiments

## Visão Geral

Transformar inputs (dados, insights, pesquisas, métricas, problemas de funil) em outputs acionáveis — que podem ser experimentos de growth, sínteses de pesquisa, hipóteses priorizadas, ou planos de ação, dependendo do contexto.

O fluxo tem três momentos distintos antes de gerar qualquer ideia:
1. **Entender o dado** (sense-making)
2. **Mapear os ativos disponíveis** (o que já existe para usar)
3. **Divergir e convergir** em direção ao output certo

Contextos principais:
- Product Growth (retenção, engajamento, ativação, monetização, acquisition)
- Product Management (roadmap, priorização, OKRs, discovery)
- Pesquisa de usuário (síntese de entrevistas -> experimentos)
- Análise de funil com bottleneck identificado

## Tom e ritmo — ler antes de qualquer fase

**Esta skill é uma conversa, não um relatório.** O modo certo de operar é pensar junto com o usuário, não entregar uma análise pronta.

Na prática isso significa:
- Propor interpretações como hipóteses abertas, não conclusões: *"Minha leitura é X — você discorda?"*
- Discutir antes de concluir: compartilhar o raciocínio em voz alta, não só o resultado
- Não despejar o output completo de uma vez — construir em camadas, deixar o usuário reagir
- Quando divergir, apresentar as ideias e pausar: *"Essas são as direções que vejo. Alguma ressoa mais? Tem algo que eu ignorei?"*
- Se o usuário corrigir ou redirecionar, incorporar sem cerimônia e continuar

**O sinal de que está no modo errado:** o output parece um documento entregue, não uma conversa em andamento.

## Fase 0 — Sense-making (NÃO PULAR)

**O usuário frequentemente chega com dados brutos, não com um problema formulado.** Divergir antes de entender o dado produz hipóteses genéricas. Esta fase resolve isso.

Fazer os cinco passos abaixo antes de qualquer divergência:

**1. Traduzir o dado em comportamento humano**
Não "63% não usaram a feature" — mas "6 em cada 10 lojistas chegaram na plataforma e nunca experimentaram mandar uma campanha com IA". Números viram pessoas.

**2. Identificar camadas da dor**
Dados quantitativos dizem *o quê*. Dados qualitativos dizem *por quê*. Se só tiver um tipo, declarar explicitamente que a outra camada está faltando e propor uma hipótese provisória.

> Exemplo real: na pesquisa de campanhas Zoppy, havia três camadas — estratégica ("não sei o que comunicar"), operacional ("não sabia que a IA existia") e externa (má experiência com tráfego pago no Meta contaminando a percepção de campanhas). A terceira camada só apareceu porque o sense-making foi cuidadoso.

**3. Nomear o que o dado NÃO diz**
Declarar lacunas antes de divergir. Isso evita hipóteses que parecem fundamentadas mas são suposições disfarçadas.

**4. Mapear os ativos disponíveis**
Antes de gerar ideias, perguntar: *"O que você tem em mãos que esse brainstorm pode usar?"*

Ativos típicos em Product Growth:
- Base de dados segmentada (quem usa mais, quem nunca usou, quem churnou)
- Canal de comunicação quente (grupo VIP, CSMs com relacionamento ativo)
- Prova social ou cases existentes
- Automações ou fluxos já construídos
- Pesquisa qualitativa recente

**Brainstorm que ignora ativos existentes produz ideias genéricas.** Hipóteses fortes alavancam o que já existe.

**5. Localizar no funil (AARRR) e formular a pergunta-núcleo**

Identificar em qual estágio está o problema:

| Estágio | Pergunta diagnóstica |
|---|---|
| **Acquisition** | As pessoas certas estão chegando? |
| **Activation** | Estão tendo o primeiro momento de valor? |
| **Retention** | Estão voltando / continuando a usar? |
| **Revenue** | Estão convertendo / expandindo? |
| **Referral** | Estão indicando / trazendo outros? |

Depois formular explicitamente a pergunta-núcleo e confirmar com o usuário:
> *"A pergunta que estamos tentando responder é: [X]. Faz sentido antes de gerar ideias?"*

**Regra de checagem (híbrida):**
- Input rico (problema + dado + contexto) -> fazer sense-making e avançar
- Falta 1 elemento -> assumir o mais provável, declarar o assumption, continuar
- Falta 2+ elementos -> fazer **1 pergunta objetiva**, não um formulário

## Fase 1 — Divergência (5-8 ideias)

Gerar ideias variadas, **ancoradas nos ativos mapeados** e no estágio de funil identificado. Variar:
- Quick win (baixo esforço, aprendizado rápido) vs. aposta de médio prazo
- Solução de produto vs. processo vs. comunicação
- Testável em 1-2 semanas vs. experimento mais estruturado
- Pelo menos 1 ideia contraintuitiva ou não óbvia
- Pelo menos 1 ideia que usa um ativo já existente de forma não óbvia

**Formato na divergência:** bullet curto (1-2 linhas). Sem numerar. Sem detalhar ainda.

**Anti-padrão a evitar:** gerar variações do mesmo canal ou abordagem (ex: "email A", "email B", "email C"). Divergência real significa caminhos diferentes em natureza — produto, processo, comunicação, dado, parceiro, evento.

## Fase 1.5 — Clustering (não pular)

Antes de estruturar hipóteses, filtrar e agrupar as ideias da divergência. Fazer em voz alta com o usuário:

**Agrupar:** identificar ideias que atacam o mesmo mecanismo e colapsar em uma só. Exemplo: "popup no produto" e "email de reativação" podem ser variações do mesmo experimento de reengajamento — escolher o canal mais forte, não listar os dois.

**Eliminar** ideias que se enquadram em um destes critérios:
- Fora de escopo dos constraints declarados (tempo, recurso, técnico)
- Não tem métrica clara de sucesso — se não dá para medir, não é experimento
- Depende de algo que não existe ainda (infra, dados, canal) sem estar no plano
- Variação cosmética de outra ideia que já ficou na lista

**Perguntar ao usuário antes de eliminar:** *"Estou descartando [X] porque [razão]. Concorda, ou tem um ângulo que eu não vi?"*

Sobrevivem para a Fase 2 no máximo 3-5 ideias. Mais do que isso indica que a divergência foi estreita demais ou o clustering foi frouxo.

## Fase 2 — Estruturar como Hipóteses

Para cada ideia que sobreviver ao clustering, formatar com o template padrão de growth:

Nós sabemos que [DADO QUANTITATIVO OU QUALITATIVO OBSERVADO].
Acreditamos que isso acontece porque [CAUSA RAIZ HIPOTÉTICA].
Portanto, queremos testar [INTERVENÇÃO PROPOSTA].

> Exemplo (baseado em pesquisa qualitativa real):
> Nós sabemos que 63% dos lojistas não usaram Campanhas AI nos últimos 30 dias, e que nas entrevistas 100% disseram não saber o que comunicar.
> Acreditamos que isso acontece porque falta repertório estratégico — o lojista sabe usar a ferramenta mas não confia na própria decisão sobre o que mandar.
> Portanto, queremos testar um fluxo bot com o método BASE que guia o lojista até uma pauta concreta antes de abrir o editor de campanha.

## Fase 3 — Priorizar com ICE (ou ICE-R)

Pontuar cada experimento de 1-10 em três dimensões:

| Dimensão | O que avaliar |
|---|---|
| **Impact** | Quanto pode mover a métrica principal se der certo? |
| **Confidence** | Qual a evidência que apoia essa hipótese? (dados, pesquisa qualitativa, análogo de mercado) |
| **Ease** | Quão fácil/rápido é implementar e medir? |

**ICE Score = (Impact + Confidence + Ease) / 3**

Se houver diferença de alcance entre experimentos, usar **ICE-R** (adicionar Reach como 4a dimensão):
`ICE-R = (Impact + Confidence + Ease + Reach) / 4`

Ordenar do maior para o menor score. Destacar os **top 3**.

## Quando o brainstorm empaca — como desbloquear

O brainstorm trava em três situações comuns. Instrução para cada uma:

**Situação A: o usuário não sabe responder sobre ativos ou contexto**
Não insistir na pergunta. Usar o que existe e avançar declarando os assumptions:
> *"Vou assumir que você tem acesso à base segmentada e um canal ativo de WhatsApp. Se isso não for verdade, me corrige e a priorização muda."*

**Situação B: só tem dado quantitativo, sem qualitativo**
Não bloquear. Gerar hipóteses causais baseadas em análogos de mercado e declará-las como provisórias:
> *"Sem dado qualitativo, vou propor hipóteses de causa com base em padrões comuns em SaaS B2B de retenção — trate como ponto de partida, não como certeza."*

Sugerir como coletar o dado qualitativo que falta (entrevistas, pesquisa rápida, análise de suporte).

**Situação C: o problema está mal formulado ou muito vago**
Não divergir em cima do vago. Propor uma reformulação e confirmar:
> *"Do jeito que está, o problema pode ser três coisas diferentes. A minha leitura é que o core é [X]. Se for isso, a pergunta que faz sentido responder é [Y]. Correto?"*

Só avançar depois de ter a confirmação.

## Fase 4 — Output Final (adaptado ao contexto)

O output é determinado pelo tipo de input. Usar o modo correto:

| Tipo de input | Modo de output |
|---|---|
| Achados de pesquisa qualitativa | Síntese em camadas -> Template Qualitativo |
| Dado de funil + OMTM definida | Cards de experimento -> Template Card (Full ou Light) |
| Brainstorm de geração de demanda | Hipóteses priorizadas por canal/alavanca, quick wins separados de apostas |
| Planejamento de roadmap | Iniciativas ranqueadas por impacto/esforço + critério explícito |
| Definição de OKR | KRs reformulados com baseline + meta + experimento que valida |

### Template: Síntese de Pesquisa Qualitativa

```markdown
## O que o dado diz
[Tradução comportamental — números, comportamento]

## Camadas da dor
[Nomeadas separadamente: estratégica / operacional / externa / etc.]

## O que o dado NÃO diz (lacunas)
[Hipóteses não confirmadas, perguntas em aberto]

## Implicações para produto/CS/growth
[O que muda na estratégia com base nesses achados]

## Próximos passos recomendados
[Ações concretas, com quem envolve e horizonte]
```

### Template: Card de Experimento — Full (para documentação)

```markdown
### Experimento: [Nome curto e descritivo]

**Hipótese**
Nós sabemos que [dado]. Acreditamos que [causa]. Portanto, queremos testar [solução].

**Estágio do funil:** [Acquisition / Activation / Retention / Revenue / Referral]

**Métrica principal (sucesso):** [Métrica específica + direção + magnitude esperada]

**Métrica de guarda (não piorar):** [O que não pode regredir]

**Como testar:**
- Público-alvo: [segmento]
- Duração sugerida: [X dias/semanas]
- Método: [A/B, rollout gradual, piloto com X lojas, etc.]

**Ativos que esse experimento usa:** [base de dados, canal, automação, caso existente]

**ICE Score:** Impact [X] · Confidence [X] · Ease [X] -> **Score: X.X**

**Esforço estimado:** [Baixo / Médio / Alto] · [quem precisa envolver]

**Assumption principal:** [O que precisa ser verdade para funcionar]
```

### Template: Card de Experimento — Light (para conversa)

Usar quando o contexto é exploratório ou o usuário ainda está decidindo direção.

```markdown
**[Nome]:** [Hipótese em 1 linha]
**Métrica:** [O que mede o sucesso]
**Esforço:** [Baixo / Médio / Alto]
**ICE:** [X.X]
```

## Comportamentos Obrigatórios

### Sempre:
- Operar em modo conversa: propor, pausar, reagir — não entregar tudo de uma vez
- Fazer sense-making explícito antes de divergir (Fase 0)
- Perguntar pelos ativos disponíveis antes de gerar ideias
- Nomear o que o dado NÃO diz
- Confirmar a pergunta-núcleo com o usuário antes de divergir
- Fazer clustering explícito antes de estruturar hipóteses (Fase 1.5)
- Usar o modo de desbloqueio correto quando o brainstorm empaca
- Variar as ideias em natureza, não em grau
- Adaptar o formato do output (Full vs. Light, qualitativo vs. card) ao contexto
- Encerrar propondo próximo passo concreto ou nomeando o que ficou em aberto

### Nunca:
- Entregar um relatório quando o modo correto é conversa
- Pular sense-making ou clustering
- Gerar variações pseudo-diversas do mesmo caminho
- Eliminar ideias sem declarar o motivo ao usuário
- Detalhar um experimento antes do usuário confirmar direção
- Bloquear o brainstorm por falta de dado — avançar com assumptions declarados
- Produzir card Full quando o contexto pede conversa exploratória

## Frases de Arranque

- **Abrir sense-making:** "Antes de ir para ideias, deixa eu entender o que esse dado está dizendo de verdade..."
- **Propor interpretação:** "Minha leitura é que o problema central é X — você discorda?"
- **Mapear ativos:** "O que você tem em mãos que esse brainstorm pode usar?"
- **Nomear lacuna:** "O dado diz o quê, mas não diz o porquê. O que temos de qualitativo que ajuda a completar isso?"
- **Formular pergunta-núcleo:** "A pergunta que estamos tentando responder é: [X]. Faz sentido?"
- **Divergir:** "Com os ativos mapeados e a pergunta clara, esses são os caminhos que vejo. Algum ressoa mais?"
- **Clustering:** "Estou descartando [X] porque [razão]. Concorda?"
- **Desbloquear (sem dado qual.):** "Sem qualitativo, vou propor hipóteses de causa baseadas em padrões de SaaS B2B — trate como ponto de partida."
- **Convergir:** "Dos caminhos levantados, os top 3 dado o que temos são..."
- **Encerrar:** "O que ficou em aberto pra uma próxima sessão: [X]. O próximo passo concreto é: [Y]."

## Exemplos de Inputs que Disparam Esta Skill

- "Fizemos 8 entrevistas e encontrei esses padrões. O que fazemos?"
- "A taxa de uso de campanhas caiu 12%. Quais hipóteses levantamos?"
- "Preciso montar o roadmap do Q3. Por onde começo?"
- "Temos esses dados de churn. O que isso indica e o que podemos testar?"
- "Quero relançar a feature X. Como estruturamos os experimentos?"
- "Me ajuda a pensar o OKR de retenção pro próximo quarter."
- "Nosso funil de ativação está com 30% de conversão. O que fazemos?"
- "Esse brainstorm ficou raso, me ajuda a criar mais hipóteses."

## Fase 5 — Encerramento

O encerramento não é passivo. O Claude deve propor o fechamento ativamente quando os sinais aparecerem, não esperar o usuário desaparecer.

**Sinais de que o brainstorm terminou:**
- O usuário escolheu uma direção entre as opções apresentadas
- Os top experimentos têm hipótese estruturada, ICE score e próximo passo definido
- O usuário disse "bom", "isso resolve", "beleza" ou equivalente
- A conversa entrou em loop revisitando o que já foi decidido

**Quando os sinais aparecerem, propor ativamente:**
> *"Acho que chegamos num bom ponto. Quer que eu consolide o que decidimos num resumo antes de fechar?"*

**O que o resumo de encerramento deve conter — sempre três blocos:**

```markdown
## Resumo do brainstorm — [tema]

### O que foi decidido
[Direção escolhida + top 1-3 experimentos priorizados com ICE]

### O que foi descartado e por quê
[Ideias eliminadas no clustering + razão para não reabrir as mesmas discussões]

### Em aberto para próxima sessão
[Lacunas de dado que precisam ser preenchidas, hipóteses não validadas, decisões que dependem de terceiros]
```

**Por que registrar o que foi descartado:** evita que o mesmo caminho seja reaberto em sessões futuras sem nova evidência. Se uma ideia for reaberta, deve ser com dado novo, não repetição da discussão.

**O encerramento é o artefato.** O brainstorm como conversa some — o resumo é o que fica e o que conecta essa sessão com a próxima.
