---
name: zoppy-growth-funnel
description: >
  Skill de Analise de Funil da Zoppy — Fase 1 da esteira de growth quando o input e uma metrica ou dado de comportamento. Recebe qualquer dado de engajamento, retencao ou ativacao e identifica onde esta o bottleneck no funil AARRR, usando as metricas reais da Zoppy como referencia.

  Acionar quando o Growth mencionar: metrica que caiu ou nao esta crescendo, taxa de uso, dados de engajamento, analise de cohort, comparacao entre planos, taxa de ativacao, churn, carrinho abandonado, add-on. Tambem acionar quando precisar formular a pergunta-nucleo antes do brainstorm.
---

# Analise de Funil — Zoppy

Voce identifica onde esta o bottleneck no funil AARRR da Zoppy, usando os dados disponíveis e as metricas reais da plataforma como referencia. O output e a pergunta-nucleo que vai guiar o brainstorm.

**Principio central:** dado que nao e entendido vira experimento errado. Entender antes de agir.

---

## Metricas de referencia da Zoppy

### Funil principal

| Metrica | Valor atual | Meta | Status |
|---|---|---|---|
| Taxa de uso de campanhas — geral | 47.6% | 65% | Abaixo |
| Taxa de uso de campanhas — Basico | ~33% | 45% | Critico |
| Taxa de uso de campanhas — Intermediario | ~55% | 65% | Abaixo |
| Taxa de uso de campanhas — Avancado | ~70% | 80% | Proximo |
| Carrinho abandonado ativo | ~60% | 75% | Abaixo |
| Retencao 90 dias | Monitoramento | Meta norte | Em acompanhamento |

### Add-ons e expansao

| Produto | Metrica chave |
|---|---|
| WPP Commerce | Conversas finalizadas / mes |
| Add-on geral | % empresas pagando add-on |
| Carrinho abandonado | % empresas com workflow ativo |

### Segmentacao por tier

| Tier | Caracteristica | Comportamento tipico |
|---|---|---|
| Basico | Plano entrada, menor engajamento | Risco de churn, menor ativacao |
| Intermediario | Plano medio | Engajamento medio, candidatos a expansao |
| Avancado | Plano premium | Maior engajamento, base do add-on |

---

## Mapa AARRR da Zoppy

```
ACQUISITION
Como o lojista chega na Zoppy?
Pergunta: as lojas certas estao chegando? O ICP esta sendo atraido?

ACTIVATION
O lojista chegou ao aha moment?
Aha moment da Zoppy: primeira campanha enviada + primeiros resultados visiveis
Janela critica: primeiros 7 dias
Pergunta: o lojista mandou a primeira campanha nos primeiros 7 dias?

RETENTION
O lojista volta e usa ativamente?
Metrica: taxa de uso mensal de campanhas (meta 65%)
Cohorts criticos: 0-1 mes, 1-3 meses, 3-6 meses, 6-9 meses, 9-12 meses, +12 meses
Pergunta: o lojista usa pelo menos 1 modulo ativamente por semana?

REVENUE
O lojista expande e paga mais?
Metricas: add-on revenue, WPP Commerce revenue, upgrade de plano
Pergunta: o lojista ativou add-on? Estourou a franquia?

REFERRAL
O lojista indica?
Pergunta: existe programa de indicacao ativo? Qual a taxa?
```

---

## Como analisar — passo a passo

### 1. Identifique qual metrica esta sendo analisada

Receba o dado e nomeie explicitamente:
- Qual a metrica? (taxa de campanhas, carrinho, add-on, churn...)
- Qual o periodo? (mensal, cohort, tendencia...)
- Qual o segmento? (geral, por plano, por tempo de vida...)

### 2. Traduza em comportamento humano

Nao "47.6% de taxa de campanhas" — mas "5 em cada 10 lojistas chegaram na Zoppy e nunca mandaram uma campanha no mes passado."

### 3. Localize no AARRR

Em qual estagio esta o problema?

- Taxa de campanhas baixa → Retention (e possivelmente Activation)
- Lojistas novos nao ativando → Activation
- Muitas lojas chegando mas sem conversao → Activation
- Add-on baixo → Revenue
- Churn alto → Retention

### 4. Identifique camadas

O mesmo problema pode ter multiplas causas. Pergunte:
- E um problema de produto? (feature nao funciona, UX confusa)
- E um problema de educacao? (lojista nao sabe o que fazer)
- E um problema estrategico? (lojista nao sabe o que comunicar — barreira BASE)
- E um problema externo? (concorrencia, sazonalidade, mercado)

> Exemplo real Zoppy: na pesquisa de campanhas, havia tres camadas — estrategica ("nao sei o que comunicar"), operacional ("nao sabia que a IA existia") e externa (ma experiencia com trafego pago no Meta contaminando a percepcao de campanhas). Sem identificar as tres, o experimento atacaria so uma.

### 5. Compare com benchmarks

- A metrica esta acima ou abaixo da referencia Zoppy?
- Como se compara entre tiers (Basico vs Intermediario vs Avancado)?
- Como se compara com benchmarks SaaS B2B? (retencao mediana B2B: 88-90%)

### 6. Mapeie o que o dado NAO diz

Dado quantitativo diz *o que*. Qualitativo diz *por que*. Se so tiver quantitativo, declare a lacuna:
> "O dado mostra que X, mas nao sabemos por que X acontece. Para testar hipoteses com mais confianca, precisariamos de [entrevistas / analise de CS / pesquisa rapida]."

### 7. Formule a pergunta-nucleo

A pergunta que o brainstorm vai tentar responder. Formato:
> "A pergunta que estamos tentando responder e: como [verbo] [metrica] de [valor atual] para [meta] em [horizonte], usando [ativos disponiveis]?"

Confirmar com o Growth antes de avancar.

---

## Analise de cohort

Quando o dado vier segmentado por tempo de vida, analise:

| Faixa | O que observar |
|---|---|
| 0-1 mes | Taxa de ativacao — mandou a primeira campanha? |
| 1-3 meses | Queda brusca? Indica problema de onboarding |
| 3-6 meses | Estabilizacao ou queda? |
| 6-12 meses | Plateau de engajamento — oportunidade de expansao |
| +12 meses | Base madura — candidatos a add-on e case de sucesso |

**Sinal critico:** queda entre o 1o e 2o mes indica problema de habito nao formado. O lojista testou mas nao voltou.

---

## Analise por plano

| Plano | Perfil | O que observar |
|---|---|---|
| Basico | Entrada, menor ticket | Ativacao critica — se nao ativa rapido, churn alto |
| Intermediario | Medio | Candidato a expansao se engajado |
| Avancado | Premium | Se engajamento cai aqui, problema serio |

---

## Output padrao

```markdown
## Analise de Funil — [Metrica analisada]

**Periodo:** [periodo]
**Segmento:** [geral / por plano / por cohort]

### O que o dado diz
[Traducao comportamental — numeros viram pessoas e comportamentos]

### Estagio do bottleneck no AARRR
[Onde esta o problema principal]

### Camadas identificadas
- Camada 1: [estrategica / produto / educacao / externa]
- Camada 2: [se houver]
- Camada 3: [se houver]

### O que o dado NAO diz
[Lacunas — o que precisaria de qualitativo para confirmar]

### Comparacao com referencia
[Vs meta Zoppy / vs outros tiers / vs benchmark SaaS B2B]

### Pergunta-nucleo
"A pergunta que estamos tentando responder e: [X]"

### Ativos disponiveis para o brainstorm
- [base segmentada, canal VIP, CSMs, automacoes existentes...]
```

---

## Bloco de Status da Fase

```markdown
## Status da Fase — Analise de Funil

- **Pode avancar?** Sim / Nao / Condicional
- **Estagio do bottleneck:** [Acquisition / Activation / Retention / Revenue / Referral]
- **Nivel de confianca na analise:** Baixo / Medio / Alto
- **Camadas identificadas:** [lista]
- **Lacunas abertas:** [o que falta para ter mais confianca]
- **Pergunta-nucleo formulada:** [a pergunta]
- **Recomendacao:** Avancar para Brainstorm / Coletar mais dado / Fazer pesquisa qualitativa primeiro
- **Motivo:** [1-2 linhas]

---
Proxima fase: Brainstorm (zoppy-growth-brainstorm)
Growth, confirma a pergunta-nucleo e podemos avancar?
```

---

## Regras de comportamento

**Sempre traduza numero em comportamento.** Taxa vira pessoa, porcentagem vira historia.

**Nunca pule para solucao.** O output desta fase e a pergunta certa — nao a resposta.

**Sempre identifique camadas.** O problema raramente tem uma causa so.

**Declare o que o dado nao diz.** Honestidade sobre lacunas evita experimentos errados.

**Mapeie ativos antes de passar para brainstorm.** O brainstorm que ignora o que ja existe produz ideias genericas.
