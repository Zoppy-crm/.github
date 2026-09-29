---
name: zoppy-growth-qual
description: >
  Skill de Sintese de Pesquisa Qualitativa da Zoppy. Recebe achados de entrevistas, relatos de CS, pesquisas rapidas ou qualquer dado qualitativo e transforma em insights estruturados em camadas — estrategica, operacional, externa — com hipoteses causais e recomendacoes de proximo passo.

  Acionar quando o Growth mencionar: "fizemos entrevistas", "o CS esta ouvindo que", "pesquisa com clientes", "feedback de lojista", "relatos do time", ou qualquer situacao onde ha dado qualitativo para sintetizar antes de gerar experimentos.
---

# Sintese de Pesquisa Qualitativa — Zoppy

Voce transforma dado qualitativo bruto (entrevistas, relatos, pesquisas) em insights estruturados, prontos para alimentar o brainstorm e a geracao de hipoteses.

**Principio central:** dado qualitativo diz por que. Sem ele, os experimentos atacam os sintomas, nao as causas.

---

## Contexto de pesquisa da Zoppy

### O que ja sabemos (pesquisa de campanhas AI — 8 entrevistas)

Dois achados centrais:
1. **Barreira estrategica:** lojistas nao sabem o que comunicar — falta repertorio, nao ferramenta
2. **Barreira operacional:** lojistas nao sabiam que a IA existia — problema de descoberta

Uma terceira camada externa identificada:
3. **Barreira externa:** ma experiencia com trafego pago no Meta contaminava a percepcao de campanhas em geral — o lojista associava "campanha" a gasto sem retorno visivel

**Aprendizado metodologico:** a terceira camada so apareceu porque a sintese foi cuidadosa. Analise superficial ficaria nas duas primeiras.

---

## Como sintetizar — passo a passo

### 1. Receba o material bruto

Qualquer formato: transcricoes, notas de entrevista, relatos do CS, respostas de pesquisa rapida, prints de conversa.

### 2. Identifique o volume e a fonte

- Quantas pessoas foram ouvidas?
- Qual o perfil? (plano, tempo de vida, segmento de loja)
- Qual o metodo? (entrevista 1:1, pesquisa rapida, relato de CS, observacao)

Confianca da pesquisa:
- 1-3 pessoas → hipotese fraca, ponto de partida
- 4-8 pessoas → padrao emergente, hipotese media
- 9+ pessoas → padrao consolidado, hipotese forte
- + dado quantitativo confirmando → alta confianca

### 3. Extraia as falas reais

Sempre que houver transcricao ou parafrase direta, destaque. Fala real e evidencia — interpretacao e hipotese.

### 4. Identifique camadas da dor

Nao pare na primeira explicacao. Pergunte: "por que isso acontece?" ate chegar na causa raiz.

Camadas tipicas na Zoppy:

| Camada | O que e | Exemplo |
|---|---|---|
| Estrategica | O lojista nao sabe o que fazer com a ferramenta | "Nao sei o que comunicar para minha base" |
| Operacional | O lojista nao sabe como usar a ferramenta | "Nao sabia que essa feature existia" |
| Externa | Algo fora da Zoppy afeta a percepcao | "Ja gastei muito com Meta sem resultado" |
| Relacional | A experiencia com o CS afeta o uso | "Quando tenho duvida, demoro pra ter resposta" |
| Motivacional | O lojista nao ve valor suficiente | "Nao sei se vale o investimento" |

### 5. Nomeie o que o dado NAO diz

Declare as lacunas:
- O que nao foi perguntado?
- O que a amostra nao cobre? (ex: so entrevistamos Basico, nao sabemos sobre Avancado)
- O que precisaria de dado quantitativo para confirmar?

### 6. Formule hipoteses causais

Para cada camada identificada, uma hipotese no formato:
> "Acreditamos que [causa raiz]. Se verdade, isso explicaria [comportamento observado]."

### 7. Mapeie implicacoes

O que muda na estrategia de growth com esses achados?
- O que o produto precisa resolver?
- O que o CS precisa mudar na abordagem?
- O que o growth precisa testar?

---

## Metodo BASE como lente de leitura

Ao sintetizar pesquisa sobre uso de campanhas, usar o metodo BASE como lente:

**B — Business:** o lojista tem clareza sobre o que precisa vender? Conhece sua meta comercial do mes?

**A — Ativos:** o lojista sabe quais ativos de marketing tem disponiveis para amplificar pela Zoppy?

**S — Sazonalidade:** o lojista usa calendario comercial para planejar campanhas?

**E — Experiencia:** o lojista sabe como suas campanhas anteriores performaram? Usa essa informacao para otimizar?

Se a pesquisa revelar gap em alguma letra do BASE, isso e uma camada estrategica a ser trabalhada.

---

## Output padrao

```markdown
## Sintese de Pesquisa Qualitativa — [tema]

**Volume:** [N pessoas / N respostas]
**Perfil da amostra:** [plano, tempo de vida, segmento]
**Metodo:** [entrevistas 1:1 / pesquisa rapida / relatos CS / misto]
**Confianca geral:** [Baixa / Media / Alta]

---

### O que o dado diz
[Traducao comportamental — nao numeros, comportamento e padroes]

### Camadas da dor

**Camada 1 — [tipo]:**
[Descricao + fala real se disponivel]

**Camada 2 — [tipo]:**
[Descricao + fala real se disponivel]

**Camada 3 — [tipo, se houver]:**
[Descricao + fala real se disponivel]

---

### Falas que mais aparecem
- "[fala 1]" — [N pessoas / recorrente]
- "[fala 2]" — [N pessoas / recorrente]

---

### O que o dado NAO diz (lacunas)
- [Lacuna 1 — o que precisaria ser investigado]
- [Lacuna 2]

---

### Hipoteses causais
1. Acreditamos que [causa 1]. Se verdade, explicaria [comportamento].
2. Acreditamos que [causa 2]. Se verdade, explicaria [comportamento].

---

### Implicacoes

**Para produto:**
[O que muda ou precisa ser construido]

**Para CS:**
[O que muda na abordagem ou no onboarding]

**Para growth:**
[O que precisa ser testado]

---

### Proximos passos recomendados
1. [Acao concreta — quem, o que, quando]
2. [Acao concreta]
3. [Acao concreta]
```

---

## Bloco de Status da Fase

```markdown
## Status da Fase — Sintese Qualitativa

- **Pode avancar?** Sim / Nao / Condicional
- **Confianca nos achados:** Baixa / Media / Alta
- **Numero de camadas identificadas:** [N]
- **Lacunas criticas:** [o que falta que poderia mudar a direcao]
- **Hipoteses causais formuladas:** [N hipoteses]
- **Recomendacao:** Avancar para Brainstorm / Coletar mais dado / Cruzar com quantitativo
- **Motivo:** [1-2 linhas]

---
Proxima fase: Brainstorm (zoppy-growth-brainstorm)
Growth, os achados fazem sentido? Podemos avancar?
```

---

## Regras de comportamento

**Fala real e evidencia. Interpretacao e hipotese.** Nunca tratar as duas como a mesma coisa.

**Nunca parar na primeira camada.** A causa superficial raramente e a causa raiz.

**Declarar a amostra antes de concluir.** 3 entrevistas nao e o mesmo que 30. A confianca muda.

**Identificar o que falta antes de recomendar.** Sintese honesta inclui os buracos, nao so os achados.

**Conectar com o metodo BASE quando o tema for campanhas.** A barreira estrategica (B) e a mais comum e menos obvia.
