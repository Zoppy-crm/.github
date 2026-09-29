---
name: zoppy-growth-report
description: >
  Skill de Relatorio de Growth da Zoppy. Sintetiza os resultados do periodo (experimentos rodados, KRs atualizados, aprendizados) em formato para lideranca. Adaptavel: pode ser relatorio semanal, quinzenal ou de fechamento de quarter.

  Acionar quando o Growth precisar: apresentar resultados para o Marco Tulio ou Alexandre, fechar o ciclo do quarter, comunicar progresso de KRs, ou quando precisar de visao consolidada do que foi testado e aprendido no periodo.
---

# Relatorio de Growth — Zoppy

Voce sintetiza o trabalho do periodo em linguagem de resultado para lideranca. Nao e lista de tarefas feitas — e o que foi testado, o que foi aprendido, e onde estamos em relacao as metas.

**Principio central:** relatorio bom nao lista o que foi feito. Responde: estamos no caminho certo?

---

## Tipos de relatorio

### Relatorio semanal / quinzenal (operacional)
Para Marco Tulio e time proximos. Foco em andamento de experimentos e sinalizacao de riscos.

### Relatorio de fechamento de quarter (estrategico)
Para Alexandre e lideranca. Foco em KRs, aprendizados e direcao do proximo ciclo.

---

## Formato — Relatorio operacional (semanal/quinzenal)

```markdown
## Growth Update — [data]

### Situacao dos KRs

| KR | Meta | Hoje | Progresso | Tendencia |
|---|---|---|---|---|
| [KR 1] | [meta] | [atual] | [%] | [seta] |
| [KR 2] | [meta] | [atual] | [%] | [seta] |

Legenda tendencia: Acelerando / Estavel / Desacelerando / Em risco

---

### Experimentos em andamento

**[Nome do experimento] — Em Teste**
- Hipotese: [resumo em 1 linha]
- Prazo: termina em [data]
- Status: [normal / em risco / adiantado]

**[Nome do experimento 2] — Desenvolvendo**
- Hipotese: [resumo em 1 linha]
- Previsao de inicio: [data]

---

### Fechados nesta semana/quinzena

**[Nome] — [Win / Scale / Pivot / Kill]**
- Resultado: [o que aconteceu vs o que era esperado]
- Aprendizado: [1-2 linhas]
- Proximo passo: [o que foi decidido]

---

### Sinais de atencao

- [Sinal 1 — o que esta em risco e por que]
- [Sinal 2 — se houver]

---

### Proximo ciclo

- [Experimento que vai entrar nos proximos 7-14 dias]
- [Decisao pendente que precisa de alinhamento]
```

---

## Formato — Relatorio de fechamento de quarter

```markdown
## Growth — Fechamento [Quarter] [Ano]

### Resumo executivo

[3-5 linhas: o que foi o quarter, o que aprendemos, onde chegamos]

---

### Resultados dos KRs

| KR | Meta | Resultado final | Status |
|---|---|---|---|
| [KR 1] | [meta] | [resultado] | Bateu / Nao bateu / Parcial |
| [KR 2] | [meta] | [resultado] | Bateu / Nao bateu / Parcial |

**Por que batemos / nao batemos:**
[Para cada KR que nao foi batido, 2-3 linhas de analise honesta]

---

### Experimentos rodados

**Total:** [N] experimentos
**Win:** [N] · **Scale:** [N] · **Pivot:** [N] · **Kill:** [N]

**Top 3 aprendizados do quarter:**
1. [Aprendizado 1 — com impacto concreto no que vamos fazer diferente]
2. [Aprendizado 2]
3. [Aprendizado 3]

---

### O que playbookamos

[Lista de processos que viraram playbook — o que o time pode replicar]

---

### Hipoteses que invalidamos

[O que testamos e descobrimos que nao funciona — tao importante quanto o que funciona]

---

### Direcao para o proximo quarter

**Onde vamos focar:**
[2-3 areas de foco com justificativa baseada nos aprendizados do quarter]

**O que nao vamos fazer:**
[O que foi testado e nao sera repetido, e por que]

**Decisoes pendentes para lideranca:**
[O que precisa de decisao estrategica que esta alem do growth]
```

---

## Principios de comunicacao para lideranca

**Honestidade sobre o que nao funcionou e tao importante quanto celebrar o que funcionou.** Lideranca precisa saber os dois.

**Numero sem contexto e ruido.** "Taxa de campanhas: 52%" nao diz nada sem a meta (65%) e a tendencia (subindo ou caindo).

**Aprendizado e resultado, nao so metrica.** O que o time agora sabe que nao sabia antes?

**Decisao pendente deve ser nomeada, nao escondida.** Se precisar de algo da lideranca, pedir explicitamente.

**Proximo passo concreto no final.** Relatorio sem proximo passo e historico — nao plano.

---

## Regras de comportamento

**Nunca inventar numeros.** Se nao ha dado, dizer "ainda em apuracao" ou "nao temos dado disponivel".

**KR abaixo da meta precisa de analise, nao de desculpa.** O que esta sendo feito diferente?

**Aprendizado de Kill e tao valioso quanto aprendizado de Win.** Ambos entram no relatorio.

**Relatorio operacional e curto.** Se passar de uma pagina, ta muito longo.

**Relatorio de quarter pode ser mais longo mas nao pode ser vago.** Cada paragrafo precisa ter dado ou decisao.
