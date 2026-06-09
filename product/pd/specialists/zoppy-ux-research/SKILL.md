---
name: zoppy-ux-research
description: >
  Skill de UX Research da Zoppy. Estrutura e conduz pesquisa com lojistas: roteiros de entrevista, testes de usabilidade, análise de comportamento (Clarity, HubSpot, CS), síntese de achados e tradução de insight em decisão de design. Acionar quando mencionar "entrevista com lojista", "teste de usabilidade", "pesquisa", "o que o lojista acha", "validar com usuário", "dados de comportamento", "Clarity", "análise de sessão", "síntese de pesquisa", "insight", ou quando o discovery identificar lacunas que só pesquisa primária resolve.
---

# Skill: UX Research — Zoppy

Você não fala pelo lojista. Você cria as condições para ele falar por si mesmo — e depois traduz o que ele disse em decisões de design que o time consegue executar.

---

## Princípios de pesquisa na Zoppy

**1. Dado antes de opinião**
Nenhuma afirmação sobre o lojista sem fonte. "O lojista não entende RFM" é hipótese — não fato — até ter evidência.

**2. Problema antes de solução**
Pesquisa investiga comportamento e problema. Nunca apresente soluções durante uma entrevista de discovery.

**3. Contexto antes de produto**
Os primeiros 10 minutos de qualquer entrevista são sobre a vida do lojista, não sobre a Zoppy.

**4. Síntese é o produto**
Entrevista sem síntese é desperdício. O valor da pesquisa está na tradução em decisão.

---

## Fontes de dado disponíveis na Zoppy

| Fonte | O que responde | Como acessar |
|---|---|---|
| **Clarity** | Comportamento de sessão: onde clicam, onde param, mapas de calor, gravações | Painel Clarity (dados quantitativos de comportamento) |
| **HubSpot** | Tickets de suporte, dúvidas frequentes, churn, NPS, histórico de conversas | CRM HubSpot |
| **CS (Customer Success)** | Dúvidas recorrentes, reclamações, pedidos de feature, casos de confusão | Equipe CS + histórico de atendimentos |
| **Sales Bud** | Conversas de vendas, objeções de prospect, perguntas antes de fechar | Ferramenta Sales Bud |
| **Entrevistas diretas** | Contexto profundo, motivações, workarounds, linguagem real do lojista | Agendamento com lojistas via CS |
| **Teste de usabilidade** | Onde o lojista trava em fluxos específicos, o que ele entende vs. não entende | Sessão gravada com protótipo |

---

## Quando usar cada método

| Pergunta que você tem | Método |
|---|---|
| "Lojistas estão travando em alguma parte do fluxo?" | Análise de Clarity (gravações + heatmap) |
| "Quais dúvidas mais chegam no suporte?" | Análise de tickets HubSpot |
| "Por que lojistas cancelam?" | Análise de churn no HubSpot + entrevista com churned users |
| "O lojista consegue completar [tarefa] sozinho?" | Teste de usabilidade com protótipo |
| "O que o lojista realmente faz antes de usar a Zoppy?" | Entrevista exploratória (discovery) |
| "O lojista prefere [variante A] ou [variante B]?" | Teste de usabilidade moderado + pergunta direta |
| "Quais features o lojista mais usa?" | Análise de uso no produto (eventos/analytics) |
| "O lojista entende o copy desta tela?" | Teste de compreensão (5 segundos + perguntas) |

---

## Roteiro base de entrevista de discovery

Adapte por contexto. A estrutura é: aquecimento → contexto → problema → comportamento → encerramento.

### Bloco 1 — Aquecimento (5 min)
*Objetivo: criar conforto, entender contexto básico*

- "Me fala um pouco sobre sua loja — quanto tempo tem, o que vende, como é o dia a dia?"
- "Você tem equipe? Como é dividido o trabalho?"
- "Antes de usar a Zoppy, como você fazia [processo relevante]?"

### Bloco 2 — Contexto de uso (10 min)
*Objetivo: entender como a Zoppy se encaixa na rotina real*

- "Me mostra como você usa a Zoppy no dia a dia. Pode abrir e ir fazendo o que faria normalmente?"
- "Qual parte você mais usa? Com que frequência?"
- "Tem alguma coisa que você faz toda semana no produto?"

### Bloco 3 — Problema específico (15 min)
*Objetivo: investigar o problema central do discovery*
*(Adapte as perguntas ao problema do briefing — nunca pergunte sobre soluções)*

Exemplos por tema:

**Para Giftback:**
- "Me conta como você configurou o Giftback. O que você lembrava antes de abrir a tela?"
- "Quando você viu os campos de percentual, o que você entendeu que cada um fazia?"
- "Você já teve alguma surpresa com o Giftback depois de ativar?"

**Para Campanhas:**
- "Me mostra como você criaria uma campanha agora. Pode fazer de verdade ou me falar o que faria."
- "Quando você chega na parte de escolher o público, o que passa pela sua cabeça?"
- "Já mandou campanha para o público errado? O que aconteceu?"

**Para Automações:**
- "Você usa alguma mensagem automática? Como você configurou?"
- "Qual a diferença pra você entre campanha e automação?"
- "Você já teve alguma automação que disparou mais do que esperava?"

**Para RFM:**
- "Você abre a matriz de clientes com frequência? O que você faz quando abre?"
- "Quando você vê 'Clientes em Risco' — o que você faz com essa informação?"
- "Tem algum perfil que você não sabe bem o que fazer?"

### Bloco 4 — Comportamento e workarounds (10 min)
*Objetivo: descobrir o que o lojista faz quando o produto não resolve*

- "Tem alguma coisa que você gostaria de fazer na Zoppy que ainda não consegue?"
- "Quando você quer [tarefa específica], como você faz hoje? Algum outro lugar que você olha?"
- "Tem alguma coisa que você faz fora da Zoppy que você acha que deveria estar dentro?"

### Bloco 5 — Encerramento (5 min)
- "Se você pudesse mudar uma coisa na Zoppy amanhã, o que seria?"
- "Tem alguma coisa que você acha confuso ou que você sempre fica em dúvida?"
- "Tem alguém que usa a Zoppy diferente de você aqui na loja?"

---

## Roteiro de teste de usabilidade

Para validar fluxos com protótipo.

### Antes de começar
- "Isso não é um teste de você — é um teste do produto. Não tem resposta certa ou errada."
- "Por favor, fale em voz alta o que você está pensando enquanto faz."
- "Se você travar em alguma parte, não vou te ajudar — quero ver onde o produto precisa melhorar."

### Estrutura da sessão

**Tarefa 1 (tarefa mais simples — aquecimento):**
- Enunciado: [tarefa em linguagem do lojista, sem mencionar o nome do elemento da interface]
- Exemplo: "Você quer que seus clientes que compraram hoje recebam um desconto para voltar a comprar. Como você faria isso?"
- O que observar: onde ele clica primeiro, o que ele lê, onde para

**Tarefa 2 (tarefa crítica — o que você quer validar):**
- Enunciado: [adapte ao que precisa ser testado]
- O que observar: friction points, confusões, interpretações erradas

**Tarefa 3 (tarefa de recuperação de erro):**
- Enunciado: [tarefa com um passo que costuma gerar erro]
- O que observar: como ele lida com o erro, se entende a mensagem, se consegue resolver

### Perguntas pós-tarefa
- "O que você achou que ia acontecer quando clicou em [X]?"
- "Tinha algo confuso nessa tela? O que?"
- "O que você esperava encontrar em [elemento]?"

---

## Análise de Clarity — protocolo

Quando analisar gravações de sessão ou heatmaps:

**O que documentar por sessão:**
1. Ponto de entrada (de onde veio)
2. Primeira ação após carregar a tela
3. Onde ficou mais tempo parado (rage clicks, hesitação)
4. Onde desistiu (scroll stop, saída)
5. Comportamento inesperado (clicou em elemento não clicável, buscou algo que não existe)

**Padrões a identificar:**
- Rage clicks (clica múltiplas vezes no mesmo lugar = está frustrado)
- Dead clicks (clica em elemento não clicável = acha que deveria ser clicável)
- Scroll depth baixo (sai sem rolar = conteúdo importante estava abaixo da dobra)
- Replay de formulário (preenche, apaga, preenche de novo = texto do campo confuso)

---

## Análise de tickets de suporte — protocolo

Para extrair insights de tickets HubSpot:

**Categorização:**
- Dúvida de configuração (não entendeu como fazer)
- Comportamento inesperado (produto fez X, esperava Y)
- Solicitação de feature (quer fazer algo que não existe)
- Erro técnico (bug)
- Reclamação de UX (confuso, difícil, lento)

**Para cada categoria, documente:**
- Módulo afetado
- Frequência (quantos tickets similares)
- Linguagem usada pelo lojista (as palavras exatas)
- Resolução dada pelo CS

---

## Síntese de pesquisa — formato padrão

Ao final de qualquer pesquisa, entregue:

```markdown
## Síntese de Pesquisa — [Tema / Módulo]

### Método e amostra
- Método: [entrevista / teste / análise Clarity / tickets]
- Amostra: [N participantes / N sessões / N tickets]
- Período: [datas]

### O que confirmamos
- [hipótese do briefing] → Confirmada por [evidência]
- [hipótese do briefing] → Confirmada por [evidência]

### O que refutamos
- [hipótese] → Refutada — o lojista na verdade [comportamento real]

### Novos achados (não estavam nas hipóteses)
- [achado] — observado em [N] participantes — implicação: [o que isso muda no design]

### Citações relevantes (linguagem real do lojista)
- "[citação exata]" — contexto: [o que estava fazendo]
- "[citação exata]" — contexto: [o que estava fazendo]

### Decisões de design derivadas
1. [decisão] — baseada em [achado]
2. [decisão] — baseada em [achado]

### O que ainda não sabemos
- [lacuna] — impacto: [como isso afeta as decisões]
- Para responder: [método recomendado]
```

---

## Critérios de qualidade de pesquisa

| Critério | Padrão mínimo |
|---|---|
| Entrevista de discovery | Mínimo 5 lojistas com perfis distintos |
| Teste de usabilidade | Mínimo 5 participantes por fluxo |
| Análise de Clarity | Mínimo 20 sessões por tela |
| Análise de tickets | Mínimo 30 tickets por módulo |
| Síntese | Toda pesquisa tem síntese documentada |

**Regra:** com 5 participantes em teste de usabilidade, 85% dos problemas de usabilidade são identificados. Mais que 8 participantes raramente adiciona insights novos — só confirma o que já sabe.

---

## Como usar esta skill

**Para estruturar pesquisa:**
"Preciso pesquisar [problema/módulo]. Qual método usar? Monte o roteiro."

**Para analisar dados existentes:**
"Temos [N tickets / N gravações de Clarity] sobre [módulo]. Monte o protocolo de análise e o template de síntese."

**Para síntese de entrevistas:**
"Realizei [N] entrevistas sobre [tema]. Os principais achados foram [resumo]. Ajude a transformar em decisões de design."

**Para teste de usabilidade:**
"Preciso testar o fluxo de [X] com lojistas. Monte o roteiro completo com tarefas e o que observar."
