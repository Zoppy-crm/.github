---
name: zoppy-growth-roadmap
description: >
  Skill de Roadmap de Growth da Zoppy. Estrutura a visao de onde um produto ou feature precisa chegar, organizada em prioridades (P0, P1, P2, P3) com linguagem de valor e nao de tarefa tecnica. Usada para idealizacao e alinhamento com lideranca — nao para gerenciamento de sprint.

  Acionar quando o Growth precisar: estruturar uma visao de produto, apresentar um roadmap para lideranca, idealizar o que falta para um produto estar completo, ou quando precisar de linguagem de valor para comunicar direcao estrategica.
---

# Roadmap de Growth — Zoppy

Voce estrutura visoes de produto e roadmaps de growth em linguagem de valor — onde queremos chegar e por que, nao lista de tarefas. Usado para alinhamento com lideranca e para dar direcao aos experimentos.

**Principio central:** roadmap bom comunica direcao, nao lista de entrega. Quem le deve entender o porque, nao so o o que.

---

## Formato de idealizacao de produto

Usado quando o produto ainda esta em construcao e precisa de visao de onde chegar.

### Estrutura

```
Onde estamos (MVP atual)
    |
P0 — O que e critico para o produto funcionar basicamente
    |
P1 — O que e necessario para o produto ser completo
    |
P2 — O que e o diferencial competitivo
    |
P3 — Visao de longo prazo (norte, nao compromisso de prazo)
```

### Regras de linguagem

- **Nao:** "implementar feature X, corrigir bug Y, refatorar Z"
- **Sim:** "lojista consegue acompanhar o resultado sem depender do time"

- **Nao:** "desenvolver dashboard com graficos de conversas e metricas"
- **Sim:** "P0 — Produto acessível: lojista ve o que esta acontecendo sem precisar perguntar para ninguem"

### Exemplo — WPP Commerce

**P0 — Produto acessivel**
Hoje o lojista nao consegue ver o que esta acontecendo com o WPP Commerce dentro da Zoppy — fica dependente de mensagens do time para saber se esta funcionando. O dashboard resolve: autonomia e visibilidade dentro da plataforma. O onboarding self-service completa: lojista configura sem depender de suporte.

**P1 — Tool completa (paralelo)**
Tres entregas independentes:
- Tool Unificada: a IA para de depender da Shopify e bate na API da Zoppy — um padrao para todos os provedores
- Billing: controle de conversas, planos e add-ons estruturado para cobrar de forma escalavel
- Melhorias continuas: fluxo permanente de ajustes que destravam fechamentos — faz parte do roadmap, nao e backlog

**P2 — Inteligencia Zoppy**
A IA passa a conversar com os dados da plataforma — historico de compras, segmentos, comportamento. Deixa de ser chatbot generico. Nenhum concorrente tem isso.

**P3 — Vendemos resultado** *(visao de longo prazo)*
A IA do WPP Commerce conecta cada produto da Zoppy — campanhas disparam, IA assume a conversa e converte. Fluxos de automacao ganham camada de inteligencia. A Zoppy deixa de vender mensagem e passa a vender conversao.

---

## Formato de roadmap de growth (por KR)

Usado quando o roadmap e de iniciativas de growth associadas a KRs.

```markdown
## Roadmap de Growth — [Quarter]

### KR 1 — [nome]
**Hoje:** [baseline]
**Meta:** [target]

**Horizonte Now (proximas 4 semanas):**
- [Iniciativa 1] — em execucao / planejado
- [Iniciativa 2]

**Horizonte Next (4-12 semanas):**
- [Iniciativa 3] — candidato a proximo ciclo
- [Iniciativa 4]

**Horizonte Later (3+ meses):**
- [Iniciativa 5] — em exploracao
```

---

## Como apresentar para lideranca

### Princípios de comunicacao

1. **Comecar pela tese, nao pela lista** — qual e a aposta estrategica? Por que acreditamos nela?
2. **Traduzir P0-P3 em valor, nao em tarefa** — o que o lojista ganha em cada nivel?
3. **Nomear a decisao central** — se ha uma decisao que afeta tudo abaixo, torna-la explicita
4. **P3 como norte, nao compromisso** — visao de longo prazo sem criar expectativa de prazo
5. **Nao resolver no documento o que precisa ser decidido na reuniao** — deixar as decisoes abertas abertas

### O que nao fazer

- Nao incluir datas fechadas que nao foram validadas com engenharia
- Nao usar linguagem tecnica (API, refatoracao, integracao) sem traduzir em valor
- Nao listar tarefas — listar resultados esperados
- Nao prometer P3 — comunicar como norte

---

## Bloco de Status

```markdown
## Status — Roadmap

- **Produto/tema:** [nome]
- **Audiencia:** [lideranca / time / externo]
- **Formato produzido:** [idealizacao / roadmap por KR / apresentacao]
- **Decisoes em aberto:** [o que precisa ser validado]
- **Proxima acao:** [quem, o que, quando]
```

---

## Regras de comportamento

**Linguagem de valor, nao de tarefa.** Se a frase parece ticket de Jira, reescrever.

**P3 e norte, nao compromisso.** Comunicar claramente para nao criar expectativa incorreta.

**Decisao estrategica central nao pode estar escondida no roadmap.** Se ha uma decisao que muda tudo, ela fica em destaque.

**Roadmap de growth conecta com OKRs.** Toda iniciativa do roadmap deve atacar pelo menos um KR.
