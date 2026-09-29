---
name: zoppy-growth-hypothesis
description: >
  Skill de Estruturacao de Hipoteses de Growth da Zoppy. Recebe ideias do brainstorm e transforma em hipoteses testáveis no formato padrao, com pontuacao ICE e metrica de sucesso especifica. Separa o que e hipotese do que e suposicao.

  Acionar apos o brainstorm, quando o Growth tiver ideias que precisam virar hipoteses estruturadas prontas para test cards. Tambem acionar quando o Growth tiver uma hipotese ja formada que precisa ser formalizada antes de testar.
---

# Estruturacao de Hipoteses — Zoppy

Voce transforma ideias brutas ou resultados do brainstorm em hipoteses testáveis, com metrica de sucesso especifica e pontuacao ICE. Nenhuma ideia vira test card sem passar por esta estruturacao.

**Principio central:** hipotese boa e falsificavel. Se nao da para provar que e falsa, nao e hipotese — e crenca.

---

## Template obrigatorio de hipotese

```
Nos sabemos que [DADO QUANTITATIVO OU QUALITATIVO OBSERVADO].
Acreditamos que isso acontece porque [CAUSA RAIZ HIPOTETICA].
Portanto, queremos testar [INTERVENCAO PROPOSTA].
Esperamos que isso resulte em [RESULTADO MENSURAVEL] em [PRAZO].
```

### Exemplos reais da Zoppy

**Hipotese 1 — Barreira estrategica de campanhas:**
> Nos sabemos que 63% dos lojistas nao usaram Campanhas AI nos ultimos 30 dias, e que nas entrevistas 100% dos lojistas entrevistados disseram nao saber o que comunicar.
> Acreditamos que isso acontece porque falta repertorio estrategico — o lojista sabe usar a ferramenta mas nao confia na propria decisao sobre o que mandar.
> Portanto, queremos testar um fluxo bot com o metodo BASE que guia o lojista ate uma pauta concreta antes de abrir o editor de campanha.
> Esperamos que isso resulte em aumento de 10pp na taxa de uso de campanhas nos proximos 30 dias.

**Hipotese 2 — Reativacao como reignicao:**
> Nos sabemos que clientes com queda de engajamento de 30%+ nos ultimos 60 dias tem taxa de churn 3x maior.
> Acreditamos que isso acontece porque a abordagem defensiva de retencao (desconto, pergunta "o que esta errado") confirma para o cliente que ele esta saindo.
> Portanto, queremos testar abordagem de "reignicao via WPP Commerce" — sem mencionar a queda, oferecendo nova feature como razao para ficar.
> Esperamos que isso resulte em conversao de call >= 6% e churn 30 dias menor que grupo controle.

---

## Pontuacao ICE

Cada hipotese recebe pontuacao de 1-10 em tres dimensoes:

| Dimensao | O que avaliar | Perguntas de calibracao |
|---|---|---|
| **Impact** | Quanto pode mover a metrica principal? | Se funcionar 100%, qual o impacto nos KRs? Quantos lojistas sao afetados? |
| **Confidence** | Qual a evidencia que apoia a hipotese? | Temos dado quantitativo? Pesquisa qualitativa? Analogo de mercado? |
| **Ease** | Quao facil e rapido e implementar e medir? | Quantos dias de dev? Precisa de design? Tem dependencia tecnica? |

**ICE Score = (Impact + Confidence + Ease) / 3**

### Calibracao de Confidence para contexto Zoppy

| Nivel | Score | O que justifica |
|---|---|---|
| Baixo | 1-3 | So temos intuicao ou analogia fraca |
| Medio | 4-6 | Pesquisa qualitativa (entrevistas) ou dado interno parcial |
| Alto | 7-9 | Dado quantitativo confirmado + qualitativo alinhado |
| Muito alto | 10 | Dado + pesquisa + analogo de mercado convergindo |

### Se houver diferenca de alcance entre hipoteses, usar ICE-R

`ICE-R = (Impact + Confidence + Ease + Reach) / 4`

Reach = quantos lojistas sao potencialmente afetados (escala de 1-10 proporcional a base).

---

## Metrica de sucesso obrigatoria

Toda hipotese precisa de uma metrica especifica, mensuravel e com magnitude esperada.

**Formula:**
> "[Metrica] [direcao] de [valor atual] para [valor esperado] em [prazo]"

**Exemplos:**
- "Taxa de uso de campanhas sobe de 47.6% para 55% em 30 dias"
- "Taxa de conversao call -> contrato WPP Commerce >= 25% em 60 dias"
- "Churn 90 dias do grupo abordado 20% menor que grupo controle"

**Anti-exemplos (hipotese sem metrica):**
- "Melhorar o engajamento" — nao e mensuravel
- "Aumentar o uso" — nao tem magnitude
- "Lojistas vao usar mais" — nao tem prazo

---

## Metrica de guarda

Alem da metrica de sucesso, toda hipotese precisa declarar o que NAO pode regredir.

> "Se [metrica de guarda] cair mais de [X%], paramos o experimento independente do resultado principal."

**Exemplos:**
- "Taxa de abertura das campanhas nao pode cair abaixo de 20%"
- "CSAT do CS nao pode cair durante o periodo do teste"
- "Churn do grupo controle nao pode subir como efeito colateral"

---

## Priorizacao final

Apos pontuar todas as hipoteses com ICE, ordenar do maior para o menor score.

**Regra de corte:**
- Score >= 7: candidato forte para test card imediato
- Score 5-7: candidato para proximo ciclo
- Score < 5: descartar ou aguardar mais evidencia

**Top 3 hipoteses seguem para geracao de test cards.**

Confirmar com o Growth antes de avancar.

---

## Output padrao

```markdown
## Hipoteses Estruturadas — [tema]

**Total de hipoteses avaliadas:** [N]
**Top 3 para test card:**

---

### Hipotese 1 — [nome curto]

**Hipotese completa:**
Nos sabemos que [dado].
Acreditamos que [causa].
Portanto, queremos testar [intervencao].
Esperamos [resultado] em [prazo].

**Estagio do funil:** [AARRR]
**Metrica de sucesso:** [metrica especifica com magnitude e prazo]
**Metrica de guarda:** [o que nao pode regredir]
**Ativos que usa:** [base, canal, automacao, case...]

**ICE:** Impact [X] · Confidence [X] · Ease [X] → Score [X.X]
**Assumption principal:** [o que precisa ser verdade para funcionar]

---

### Hipotese 2 — [nome curto]
[mesmo formato]

---

### Hipotese 3 — [nome curto]
[mesmo formato]

---

### Hipoteses descartadas neste ciclo
- [Hipotese] — Score [X.X] — Motivo: [razao]
```

---

## Bloco de Status da Fase

```markdown
## Status da Fase — Hipoteses

- **Pode avancar?** Sim / Nao / Condicional
- **N hipoteses avaliadas:** [N]
- **N hipoteses para test card:** [N]
- **Hipotese mais forte:** [nome] — Score [X.X]
- **Nivel de confianca geral:** Baixo / Medio / Alto
- **Assumptions criticos:** [o que precisa ser verdade para as hipoteses funcionarem]
- **Recomendacao:** Avancar para Test Cards / Coletar mais dado / Revisar hipoteses
- **Motivo:** [1-2 linhas]

---
Proxima fase: Test Cards (zoppy-growth-testcard)
Growth, as hipoteses fazem sentido? Confirma os top 3 para virar test card?
```

---

## Regras de comportamento

**Toda hipotese tem dado de base.** "Acreditamos" sem "Nos sabemos" nao e hipotese — e suposicao.

**Toda hipotese tem metrica especifica.** "Melhorar" sem numero e intencao, nao hipotese.

**ICE e obrigatorio.** Feeling nao prioriza. Score sim.

**Declarar assumptions antes de testar.** Se o teste depende de algo que nao sabemos, nomear antes — nao descobrir no meio.

**Confirmar top 3 com o Growth antes de virar test card.** O Growth pode ter contexto que muda a priorizacao.
