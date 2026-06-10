---
name: zoppy-data-design
description: >
  Skill de Design de Dados da Zoppy. Garante que tabelas, gráficos, dashboards e métricas comunicam decisão — não apenas dado. Aplica princípios de data visualization ao contexto do lojista: hierarquia de métricas, tipo certo de gráfico para cada pergunta, tabelas com ação embutida, e formatação que o lojista entende sem ser analista. Acionar sempre que uma tela contiver tabela, gráfico, métrica, dashboard, relatório, ou quando mencionar "dado", "gráfico", "tabela", "relatório", "métrica", "visualização", "número", "ranking".
---

# Skill: Design de Dados — Zoppy

Dado sem contexto é ruído. Dado com contexto é decisão. Cada número que aparece na Zoppy precisa levar o lojista a fazer algo — ou não precisa aparecer.

---

## Princípios de data design para o lojista

**1. Dado → Decisão**
Antes de mostrar qualquer métrica, pergunte: qual decisão o lojista vai tomar com esse dado? Se a resposta for "nenhuma", o dado não precisa estar em destaque.

**2. Hierarquia antes de completude**
O dashboard não é um relatório financeiro. É um painel de controle. O que o lojista precisa saber *agora* fica no topo. O que ele pode querer *depois* fica acessível mas não disputando atenção.

**3. Contexto é obrigatório**
Um número sozinho não significa nada. R$ 12.400 é bom ou ruim? Depende do mês anterior, da meta, do benchmark. Todo número precisa de um comparador.

**4. Ação embutida**
Sempre que possível, dado com ação adjacente. "47 clientes em risco" + botão "Criar campanha para eles". Dado que não leva a lugar nenhum gera frustração.

---

## Hierarquia de métricas por módulo

### Dashboard principal

**Nível 1 — Acima da dobra, maior destaque:**
- Receita gerada pela Zoppy (com % do total)
- Percentual de retorno (clientes que voltaram)

**Nível 2 — Visíveis sem scroll, hierarquia secundária:**
- Receita total do período
- Número de vendas
- Ticket médio
- Frequência média

**Nível 3 — Gráficos e detalhamentos:**
- Faturamento mensal (linha, comparativo)
- Vendas por dia da semana (barras)
- Distribuição por canal

**Regra:** nunca mais de 4 métricas de nível 1 competindo ao mesmo tempo.

---

### Relatório de Campanha

**Nível 1:** Taxa de abertura / Taxa de clique / Conversões
**Nível 2:** Enviados / Entregues / Falhas
**Nível 3:** Tabela de clientes por status

---

### Matriz RFM

**Nível 1:** Distribuição de clientes por perfil (visual + número)
**Nível 2:** Valor total por perfil (quais valem mais)
**Nível 3:** Tabela de clientes por perfil (com filtro)

---

## Tipo certo de gráfico por pergunta

| Pergunta do lojista | Tipo de gráfico | Quando evitar |
|---|---|---|
| "Como foi meu faturamento ao longo do tempo?" | Linha (trend) | Nunca pizza |
| "Qual canal vende mais?" | Barras horizontais | Evitar pizza para mais de 4 categorias |
| "Como meus clientes estão distribuídos?" | Barras + número | Pizza só para 2-3 categorias com diferença clara |
| "Qual dia da semana vendo mais?" | Barras verticais | Nunca linha para dado sem continuidade |
| "Qual segmento RFM tem mais clientes?" | Barras horizontais + cor do segmento | Mapa de calor — lojista não lê |
| "Como meu resultado compara com o mês anterior?" | Número grande + seta + % variação | Nunca dois gráficos de linha sobrepostos |
| "Quais clientes eu devo contatar?" | Tabela com filtro + ação | Nunca gráfico — dado operacional precisa de tabela |

---

## Formatação de números para o lojista

| Tipo | Formato | Exemplo |
|---|---|---|
| Moeda grande | R$ 12,4 mil | Não R$ 12.400,00 |
| Moeda pequena | R$ 340,00 | Não R$ 340 |
| Percentual | 12% | Não 12,0% nem 0.12 |
| Variação positiva | +8% ↑ | Com cor Action/Success + seta |
| Variação negativa | -3% ↓ | Com cor Action/Critical + seta |
| Número de clientes | 1.247 clientes | Nunca "1247" |
| Data | 12 de maio | Não 12/05/2025 em contextos narrativos |
| Período | Últimos 30 dias | Não "30d" sem expansão |

---

## Padrões de tabela na Zoppy

### Tabela operacional (listas de clientes, campanhas, automações)

**Estrutura:**
- Coluna de identificação à esquerda (nome do cliente, nome da campanha)
- Colunas de dados no meio
- Coluna de ações/status à direita
- Altura de linha: mínimo 48px (acessibilidade + mobile)
- Máximo de colunas visíveis sem scroll: 5-6

**Ordenação:**
- Padrão: por data (mais recente primeiro) ou por relevância (cliente em maior risco primeiro)
- Ordenação clicável em colunas numéricas e de data
- Indicador visual de ordenação ativa

**Ações na tabela:**
- Ação primária: visível na linha (botão outline ou link)
- Ações secundárias: menu de contexto (3 pontos)
- Ação destrutiva: sempre no menu, nunca exposta na linha

**Empty state na tabela:**
- Nunca tabela vazia sem mensagem
- Linha única com orientação: o que fazer para ter dados aqui

---

### Cards de métricas (KPIs)

**Estrutura obrigatória:**
```
[Label em Caption/Label]
[Número em Large/Medium — destaque]
[Comparador: +8% vs. mês anterior em Caption + cor semântica]
[CTA opcional: "Ver detalhe" em Link]
```

**Regras:**
- Label nunca em jargão (ver glossário em `zoppy-ux-writer`)
- Comparador sempre presente (vs. período anterior ou meta)
- Sem ícone decorativo que não agrega significado
- Cor só para indicar variação (verde = positivo, vermelho = negativo) — não só para decorar

---

## Dashboard — padrões de layout

### Princípios de layout para dashboard Zoppy:

**Grade sugerida:** 12 colunas, gap 24px

| Elemento | Largura | Posição |
|---|---|---|
| Métrica principal (Receita Zoppy) | 4 colunas | Linha 1, primeiro |
| Métricas secundárias | 4 colunas | Linha 1, sequência |
| Gráfico de trend principal | 8 colunas | Linha 2 |
| Gráfico secundário | 4 colunas | Linha 2 |
| Tabela operacional | 12 colunas | Linha 3+ |

**Regras de composição:**
- Métricas grandes primeiro, gráficos depois, tabelas por último
- Filtros de período sempre no topo, visíveis sem scroll
- Loading: skeleton com o formato dos cards (não spinner genérico)
- Sem dado: empty state com instrução, não silêncio

---

## Gráficos — especificações técnicas para o DS

| Propriedade | Valor |
|---|---|
| Eixos | Cor Text/Neutral (#727C8C), Caption 12px |
| Grid lines | Surface/Gray (#F2F5F9), horizontal apenas |
| Tooltip | Surface/Default com sombra, padding 8px, Body 14px |
| Cores de série | Action/Primary → Action/Secondary → cores RFM em sequência |
| Área sob linha | Fill com 10% opacity da cor da linha |
| Barra ativa (hover) | 90% opacity + borda 1px da cor da barra |
| Sem dado em série | Linha tracejada, sem ponto |
| Legenda | Embaixo do gráfico, nunca ao lado (problema de espaço) |

---

## Checklist de design de dados — antes do handoff

### Hierarquia e decisão
- [ ] Cada métrica em destaque tem uma decisão associada
- [ ] Não há mais de 4 KPIs de nível 1 competindo
- [ ] Cada número tem comparador (período anterior, meta, benchmark)

### Tipo de gráfico
- [ ] Linha para trend temporal
- [ ] Barras para comparação categórica
- [ ] Pizza só se máximo 3 categorias
- [ ] Tabela para dado operacional com ação

### Formatação
- [ ] Moeda formatada (R$ 12,4 mil, não R$ 12400)
- [ ] Variações com seta + cor semântica
- [ ] Períodos em linguagem natural (Últimos 30 dias)

### Tabelas
- [ ] Linha mínima 48px
- [ ] Máximo 6 colunas sem scroll horizontal
- [ ] Ações destrutivas no menu, não na linha
- [ ] Empty state com orientação

### Acessibilidade de dados
- [ ] Cor não é o único diferenciador em gráficos
- [ ] Labels nas barras ou tooltips acessíveis
- [ ] Tabelas com headers descritivos

---

## Como usar esta skill

**Para novo dashboard ou tela de dados:**
"Aplique data design para [tela]. Defina: hierarquia de métricas, tipo de gráfico para cada pergunta, formatação e ação embutida."

**Para revisar visualização existente:**
"Revise essa visualização de [módulo]. O dado está levando a uma decisão? Hierarquia está correta? Tipo de gráfico é o mais adequado?"

**Para tabela específica:**
"Especifique a tabela de [lista]. Inclua: colunas, ordenação padrão, ações, empty state e comportamento mobile."
