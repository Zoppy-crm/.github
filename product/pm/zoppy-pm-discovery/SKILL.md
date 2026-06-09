---
name: zoppy-pm-discovery
description: >
  Skill de Discovery de Produto da Zoppy — Fase 3 da esteira de PM. Recebe itens qualificados e conduz o processo de entendimento profundo do problema antes de qualquer solução ser discutida. Responde as 5 perguntas obrigatórias e produz uma hipótese falsificável pronta para priorização. Dois caminhos distintos: MELHORIA começa com dado real, FEATURE começa com hipótese estratégica.

  Acionar após Qualificação completa. Também acionar quando o PM precisar aprofundar entendimento de um problema antes de priorizar, quando uma hipótese precisar ser revisada, ou quando um item voltar do roadmap com "hipótese invalidada".

  Discovery não é pesquisa por pesquisa — é reduzir incerteza antes de comprometer recursos. O output não é uma solução. É um problema entendido com profundidade suficiente para o design explorar.
---

# Discovery de Produto — Zoppy

Você conduz o entendimento profundo do problema. O PM sai do discovery sabendo exatamente o que está resolvendo, para quem, e como vai saber se funcionou. Nenhuma tela é desenhada antes desse entendimento estar claro.

**Princípio central:** o PM é dono do problema. O design é dono da solução. O discovery é o processo que garante que o problema está definido com clareza suficiente para o design fazer boas apostas.

---

## Métrica de fundo

Todo discovery precisa responder: **onde na árvore de retenção esse problema está quebrando?**

```
RETENÇÃO 90 DIAS (métrica norte)
        ↓
ATIVAÇÃO — lojista chegou ao aha moment nos primeiros 7 dias?
        ↓
ENGAJAMENTO — lojista usa ativamente pelo menos 1 módulo por semana?
        ↓
EXPANSÃO — lojista ativou mais de 1 módulo?
        ↓
SATISFAÇÃO — CS não recebe ticket de dúvida ou frustração desse lojista?
```

Um problema que quebra ativação tem prioridade diferente de um problema que gera atrito em expansão. O discovery precisa identificar onde na árvore o problema vive.

---

## Dois caminhos de discovery

### Caminho MELHORIA
O problema já está acontecendo. Existem dados reais.
Discovery começa com o que já se sabe — HubSpot, Clarity, tickets, relatos do CS — e vai fundo para entender a causa raiz, não só o sintoma.

**Pergunta de entrada:** *"O que exatamente o lojista está tentando fazer e não consegue?"*

### Caminho FEATURE
O produto não tem isso ainda. É uma aposta estratégica.
Discovery começa com a hipótese — benchmark, objetivo do CEO, pedido de fechamento — e vai validar se o problema que a feature resolve é real e relevante o suficiente para construir.

**Pergunta de entrada:** *"Se construirmos isso, qual problema real do lojista estamos resolvendo — e temos evidência de que esse problema existe?"*

---

## As 5 perguntas obrigatórias

Todo discovery — MELHORIA ou FEATURE — responde as cinco perguntas. A profundidade da resposta varia, mas nenhuma é pulada.

---

### Pergunta 1 — Qual é o problema real?
*Não o sintoma. Não a solução. O problema.*

O sintoma é o que o lojista relata. O problema real é o que está causando o sintoma.

**Técnica:** pergunte "por quê?" três vezes.
- Sintoma: "lojista não encontra o relatório de cashback"
- Por quê? → "a navegação até o relatório tem muitos passos"
- Por quê? → "o módulo de relatórios não está no menu principal"
- Por quê? → "a arquitetura de informação não reflete o que o lojista prioriza"
- Problema real: "a arquitetura de informação da Zoppy não está organizada pela prioridade do lojista"

Para FEATURE: o problema real é a necessidade estratégica que a feature atende — não a feature em si.

---

### Pergunta 2 — Para quem?
*Perfil de lojista e momento da jornada.*

Não existe "o lojista" genérico. O problema afeta perfis diferentes de forma diferente.

Responda:
- **Perfil:** qual tipo de lojista tem esse problema? (segmento, tamanho, maturidade digital, módulos que usa)
- **Momento:** em que ponto da jornada o problema aparece? (onboarding, uso recorrente, expansão, crise)
- **Frequência por perfil:** o problema é igual para todos ou mais crítico para um perfil específico?

Para FEATURE: para quem essa feature resolve um problema real? Se não conseguir responder com um perfil específico, o discovery ainda não terminou.

---

### Pergunta 3 — Qual a frequência e o impacto?
*Dado quantitativo, mesmo que estimado.*

| Fonte | Como usar |
|---|---|
| HubSpot | Volume de tickets por módulo, recorrência de relatos, perfil dos lojistas afetados |
| Dashboard interno | Taxa de uso por módulo, abandono de fluxo, tempo em tela |
| Clarity | Onde o lojista clica, onde para, onde abandona |
| CS | Padrão de atendimento, perguntas mais frequentes, tempo de resolução |

Se não há dado disponível, registre a estimativa com o nível de confiança explícito. Dado estimado com confiança baixa é melhor que ausência de dado — desde que seja honesto.

**Output esperado:** "X% dos lojistas [perfil] encontram esse problema [momento], com impacto estimado em [ativação/engajamento/expansão/satisfação]"

---

### Pergunta 4 — Qual o custo de não resolver?
*O que acontece se a gente ignorar?*

Essa pergunta força o PM a avaliar a urgência real — não a urgência percebida.

Opções de resposta:
- **Churn confirmado:** lojistas estão cancelando por causa desse problema
- **Churn em risco:** lojistas com esse problema têm taxa de churn maior que a média
- **Ativação bloqueada:** lojistas novos não chegam ao aha moment por causa disso
- **Atrito acumulado:** não causa churn imediato mas corrói satisfação ao longo do tempo
- **Oportunidade perdida:** sem isso, não conseguimos crescer em determinado segmento
- **Custo operacional:** CS está absorvendo um problema que o produto deveria resolver

Para FEATURE: custo de não resolver é a oportunidade que estamos deixando para o concorrente ou o objetivo de negócio que não conseguimos atingir.

---

### Pergunta 5 — Qual é a hipótese de solução?
*Uma frase, falsificável.*

O discovery termina com uma hipótese — não com uma solução. A hipótese é o que o time vai testar. A solução é o que o design vai explorar a partir dela.

**Formato obrigatório da hipótese:**

```
Acreditamos que [direção de solução]
vai resolver [problema real]
para [perfil de lojista] em [momento da jornada],
e saberemos que funcionou quando [métrica específica] mudar.
```

**Exemplos:**

MELHORIA:
```
Acreditamos que reorganizar a navegação principal da Zoppy
vai resolver a dificuldade do lojista em encontrar informações de resgate
para lojistas com mais de 3 meses de uso, no momento de análise de resultado,
e saberemos que funcionou quando o volume de tickets de CS sobre localização de relatórios cair 50%.
```

FEATURE:
```
Acreditamos que criar um resumo semanal automático por WhatsApp
vai resolver a falta de visibilidade do lojista sobre o desempenho do programa
para lojistas com operação de vendas ativa, no momento de acompanhamento recorrente,
e saberemos que funcionou quando o engajamento semanal com o módulo de relatórios aumentar 30%.
```

**A hipótese não é a solução.** Ela define a direção — o design vai explorar como chegar lá.

---

## Discovery mínimo vs. discovery robusto

Nem todo item precisa do mesmo nível de discovery. Calibre pela confiança que saiu da qualificação:

### Discovery mínimo (confiança média/alta na qualificação)
- Responda as 5 perguntas com os dados já disponíveis
- Pelo menos uma conversa com o CS para validar o problema
- Tempo esperado: 1-2 dias

### Discovery robusto (confiança baixa na qualificação)
- Responda as 5 perguntas com pesquisa ativa
- Pelo menos uma sessão com lojista real (entrevista ou observação)
- Cruzamento de pelo menos duas fontes de dado
- Benchmark se for FEATURE
- Tempo esperado: 1-2 semanas

### Discovery acelerado (urgência justificada)
- Quando há pressão externa legítima e tempo limitado
- Responda as 5 perguntas com o que já existe — mesmo que incompleto
- Documente explicitamente o que não foi validado e o risco associado
- O item entra no roadmap com confiança baixa documentada
- Tempo esperado: algumas horas

---

## Ritual de discovery — sessão com lojista ou CS

Para itens de alto impacto, o discovery inclui pelo menos uma sessão com uma pessoa real.

**Com CS:**
- Objetivo: entender o padrão de atendimento, a fala real do lojista, o contexto que não aparece no ticket
- Duração: 20-30 minutos
- Perguntas-chave: "Como o lojista descreve o problema?", "O que ele está tentando fazer quando aciona vocês?", "Como vocês resolvem hoje?"

**Com lojista:**
- Objetivo: observar o comportamento real, não o comportamento relatado
- Duração: 30-45 minutos
- Formato: peça para o lojista realizar uma tarefa enquanto pensa em voz alta — não faça perguntas sobre opinião
- Pergunta-chave: "Você pode me mostrar como faz X hoje?"

**Regra:** o PM vai como observador — não como vendedor da solução. O objetivo é aprender, não confirmar o que já acredita.

---

## Formato do output do discovery

```markdown
## Discovery Completo

**Data:** [data]
**Conduzido por:** PM
**Categoria:** MELHORIA / FEATURE
**Item de origem:** [referência à qualificação]

---

**Problema real:**
[Uma frase clara — não sintoma, não solução]

**Onde quebra na árvore de retenção:**
[ ] Ativação — bloqueia chegada ao aha moment
[ ] Engajamento — reduz uso recorrente
[ ] Expansão — impede adoção de novos módulos
[ ] Satisfação — corrói relação sem causar churn imediato

**Para quem:**
- Perfil: [descrição do lojista afetado]
- Momento da jornada: [quando o problema aparece]
- Intensidade por perfil: [quem sofre mais]

**Frequência e impacto:**
- Dado: [fonte + número ou estimativa]
- Confiança no dado: Baixo / Médio / Alto
- Custo de não resolver: [churn / ativação bloqueada / atrito / oportunidade perdida]

**Fontes consultadas:**
- [ ] HubSpot
- [ ] Clarity
- [ ] Dashboard interno
- [ ] CS (sessão realizada em: [data])
- [ ] Lojista real (sessão realizada em: [data])
- [ ] Benchmark

**Hipótese:**
Acreditamos que [direção de solução]
vai resolver [problema real]
para [perfil] em [momento],
e saberemos que funcionou quando [métrica] mudar.

**Nível de confiança total:** Baixo / Médio / Alto
**Tipo de discovery realizado:** Mínimo / Robusto / Acelerado
```

---

## Bloco de Status da Fase — formato obrigatório

```markdown
## Status da Fase — Discovery

- **Pode avançar?** Sim / Não / Condicional
- **Categoria do item:** MELHORIA / FEATURE
- **Onde quebra na árvore de retenção:** Ativação / Engajamento / Expansão / Satisfação
- **Nível de confiança:** Baixo / Médio / Alto
- **O que foi descoberto:**
  - [resumo das principais descobertas]
- **Hipótese:**
  - [hipótese no formato padrão]
- **Hipóteses que ainda precisam ser validadas:**
  - [lista — se vazia, escreva "Nenhuma"]
- **Lacunas abertas:**
  - [o que não foi possível responder e por quê]
- **Recomendação:** Avançar para Priorização / Revisar / Pausar
- **Motivo:** [1-2 linhas]

---
➡️ Próxima fase: Priorização (zoppy-pm-prioritization)
🙋 PM, confirma que podemos avançar para priorização?
```

---

## Regras de comportamento

**Discovery não termina com solução.** O output é uma hipótese — não um wireframe, não uma lista de requisitos, não uma tela imaginada. Se o PM chegar ao final do discovery com uma solução na cabeça, ele precisa transformá-la em hipótese antes de avançar.

**Cinco perguntas, sem exceção.** Discovery que não responde as cinco perguntas volta para observação. Não existe discovery parcial aprovado.

**Confiança baixa não bloqueia — mas precisa ser honesta.** Um discovery com confiança baixa pode avançar desde que o nível de incerteza esteja documentado. O PM está fazendo uma aposta — precisa saber disso.

**A sessão com pessoa real é insubstituível para alto impacto.** Dado de dashboard não substitui observação direta. Para itens que potencialmente afetam ativação ou causam churn, pelo menos uma sessão com CS ou lojista é obrigatória.

**Problema real ≠ sintoma.** Se o discovery terminou descrevendo o que o lojista reclamou — e não o que está causando a reclamação — não terminou.

**FEATURE sem evidência de demanda real não avança.** Uma feature bonita sem lojista que precise dela é produto para o time, não para o mercado. O discovery de FEATURE precisa encontrar a demanda real — não fabricá-la.

**Hipótese falsificável.** Se não dá para descrever como saberemos que a hipótese está errada, ela não é uma hipótese — é uma crença. O campo "saberemos que funcionou quando" é o mais importante do formato.
