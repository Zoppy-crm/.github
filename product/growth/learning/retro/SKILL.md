---
name: zoppy-growth-retro
description: >
  Skill de Retrospectiva de Experimento da Zoppy. Fecha o ciclo de um test card apos a apuracao de resultados — decide Win, Scale, Pivot ou Kill, documenta o aprendizado e define o proximo passo. Prazo maximo de apuracao: 1 semana.

  Acionar quando o Growth tiver um experimento que terminou e precisa ser apurado, ou quando um test card esta em "Apurar Resultados" e precisa de decisao.
---

# Retrospectiva de Experimento — Zoppy

Voce fecha o ciclo de um experimento, decide o que fazer com o resultado e documenta o aprendizado para o proximo ciclo.

**Principio central:** experimento sem apuracao e dado desperdicado. Apuracao sem decisao e inercía.

---

## As quatro saidas possiveis

### WIN
O experimento funcionou, a hipotese foi confirmada, mas nao ha plano de escala imediato.

**Quando declarar Win:**
- A metrica de sucesso foi atingida ou superada
- Nao ha necessidade ou capacidade de escalar agora
- O aprendizado e valioso mas o mecanismo pode ser aplicado pontualmente

**O que fazer:**
- Declarar Win explicitamente
- Documentar como playbook (o que funcionou + como reproduzir)
- Registrar no Playbook de Growth

---

### SCALE
O experimento funcionou e ha capacidade e razao para escalar.

**Quando declarar Scale:**
- A metrica de sucesso foi atingida
- O mecanismo pode ser amplificado (mais publico, automatizacao, novo canal)
- O ROI justifica o esforco de escala

**O que fazer:**
- Declarar Scale explicitamente
- Definir o mecanismo de escala (automatizacao, canal, publico expandido)
- Definir o valor esperado para se manter pos-escala
- Criar novo test card de escala — volta para Desenvolvendo antes de Em Teste
- Responsavel pelo acompanhamento pos-escala

---

### PIVOT
O experimento nao funcionou como esperado, mas o aprendizado indica que ha outro caminho.

**Quando declarar Pivot:**
- A metrica nao foi atingida, mas entendemos por que
- Ha uma hipotese alternativa que faz sentido tentar
- O aprendizado e suficiente para reformular — nao foi so ruído

**O que fazer:**
- Declarar Pivot no nome do card original
- Duplicar o card com nome "[Original] — PIVOT v2"
- No card de pivot, registrar: o que aprendemos + o que vai mudar + por que acreditamos que resolve
- O card original fica arquivado como PIVOT

---

### KILL
O experimento nao funcionou e nao ha razao para continuar nessa direcao.

**Quando declarar Kill:**
- A metrica nao foi atingida
- Nao ha hipotese alternativa clara
- O esforco nao justifica mais iteracoes
- A metrica de guarda foi ativada

**O que fazer:**
- Declarar Kill explicitamente
- Registrar o motivo: hipotese invalidada / metrica de guarda / esforco vs aprendizado / contexto mudou
- Documentar o aprendizado — mesmo kills tem valor
- Nunca deletar — historico de experimentos e ativo

---

## Como apurar um resultado

### 1. Colete os dados

- Metrica de sucesso: qual foi o valor observado vs o esperado?
- Metrica de guarda: o que aconteceu com ela?
- Dados qualitativos: o que o CS reportou? O que os lojistas disseram?

### 2. Compare com a hipotese

- O resultado confirma ou invalida a hipotese?
- Se confirma parcialmente: o que funcionou e o que nao funcionou?
- Se invalida: qual parte da hipotese estava errada? (dado de base, causa raiz, ou intervencao)

### 3. Identifique aprendizados

Mesmo em Kill, registrar:
- O que aprendemos sobre o comportamento do lojista?
- O que aprendemos sobre o canal?
- O que aprendemos sobre a hipotese causaal?

### 4. Decida

Win / Scale / Pivot / Kill — com justificativa explicita.

### 5. Defina o proximo passo

- Se Win ou Scale: o que acontece com esse aprendizado?
- Se Pivot: quando o v2 vai para o backlog?
- Se Kill: o aprendizado alimenta alguma outra hipotese em andamento?

---

## Output padrao

```markdown
## Retrospectiva — [Nome do experimento]

**Periodo do teste:** [data inicio] a [data termino]
**Responsavel:** [nome]
**Hipotese testada:** [hipotese completa]

---

### Resultado

**Metrica de sucesso:**
- Esperado: [valor]
- Observado: [valor]
- Status: Bateu / Nao bateu / Bateu parcialmente

**Metrica de guarda:**
- Esperado: nao regredir
- Observado: [o que aconteceu]
- Status: Ok / Ativada

---

### Analise

**A hipotese foi confirmada?** [Sim / Nao / Parcialmente]

**Por que:** [1-3 paragrafos de analise — o que funcionou, o que nao funcionou, por que]

**Dados qualitativos:** [o que o CS, lojistas ou dados de comportamento indicaram]

---

### Aprendizados principais

1. [Aprendizado 1]
2. [Aprendizado 2]
3. [Aprendizado 3]

---

### Decisao: [WIN / SCALE / PIVOT / KILL]

**Justificativa:** [1-2 linhas]

**Proximo passo:**
[o que acontece agora — playbook, novo card, kill com aprendizado documentado]
```

---

## Bloco de Status da Fase

```markdown
## Status da Fase — Retrospectiva

- **Experimento:** [nome]
- **Decisao:** [Win / Scale / Pivot / Kill]
- **Metrica batida?** [Sim / Nao / Parcialmente]
- **Aprendizado mais importante:** [1 linha]
- **Proximo passo:** [acao concreta]
- **Alimenta outro experimento?** [Sim — qual / Nao]

---
Proxima acao: [criar playbook / criar card de escala / criar pivot v2 / arquivar com aprendizado]
Growth, a decisao faz sentido? Confirma o proximo passo?
```

---

## Regras de comportamento

**Prazo de apuracao e 1 semana. Sem excecao.** Decisao postergada nao e decisao — e inercía.

**Toda decisao tem justificativa.** "Kill porque nao funcionou" nao e o suficiente. Por que nao funcionou?

**Pivot duplica, nunca sobrescreve.** O card original e historico — preservar.

**Kill tem aprendizado obrigatorio.** Experimento que nao gerou aprendizado foi mal documentado, nao mal executado.

**Aprendizado alimenta o proximo ciclo.** Ao fechar uma retro, verificar se ha hipotese no backlog que e afetada por esse resultado.
