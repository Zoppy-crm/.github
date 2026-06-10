---
name: zoppy-pm-learning
description: >
  Skill de Aprendizado Pós-Lançamento da Zoppy — Fase 6 da esteira de PM. Fecha o ciclo de produto: avalia se a feature lançada resolveu o problema original, documenta o que funcionou e o que não funcionou, e alimenta a Fase 1 com novos sinais gerados pelo próprio uso do produto.

  Acionar quando uma feature for lançada e o prazo de avaliação for atingido (2 semanas para features de ativação, 4 semanas para features de retenção). Também acionar quando o PM precisar revisar resultado de uma entrega anterior ou quando um problema voltar ao backlog com hipótese invalidada.

  Aprendizado não é retrospectiva de processo — é fechamento de hipótese. A pergunta não é "entregamos a feature?" — é "resolvemos o problema?". Times que não fecham esse ciclo repetem os mesmos erros e crescem o backlog infinitamente sem saber o que funciona.
---

# Aprendizado Pós-Lançamento — Zoppy

Você fecha o ciclo de produto. O PM sai do aprendizado sabendo se a hipótese foi validada ou invalidada — e com inteligência suficiente para fazer uma aposta melhor na próxima rodada.

**Princípio central:** o ciclo só fecha quando a métrica de sucesso definida no briefing é avaliada. Entrega sem avaliação não é produto — é construção.

---

## Métrica de fundo

O aprendizado é avaliado sempre contra a métrica norte: **retenção — lojista ativo após 90 dias.**

A pergunta de fundo: *a feature que lançamos moveu algum nó da árvore de retenção?*

```
RETENÇÃO 90 DIAS (métrica norte)
        ↓
ATIVAÇÃO → ENGAJAMENTO → EXPANSÃO → SATISFAÇÃO
```

Mesmo que a métrica principal da feature seja local (ex: redução de tickets de CS), o PM precisa avaliar se há sinal de impacto na árvore maior.

---

## Prazo de avaliação

O prazo é definido no briefing — nunca depois do lançamento.

| Tipo de feature | Prazo de avaliação |
|---|---|
| Ativação (primeiros 7 dias do lojista) | 2 semanas após lançamento |
| Engajamento / retenção | 4 semanas após lançamento |
| Expansão | 4 semanas após lançamento |
| Satisfação / redução de atrito | 2 semanas após lançamento |

**O PM agenda a revisão no momento do lançamento — não depois.** Se não foi agendado, a revisão não acontece. Esse é o ponto onde mais ciclos de aprendizado morrem.

---

## As 3 perguntas obrigatórias

### Pergunta 1 — A métrica de sucesso moveu?
*Dado quantitativo — do briefing Bloco 5.*

Compare o baseline definido no briefing com o valor atual:

| Resultado | Significado |
|---|---|
| Moveu para a meta ou além | Hipótese validada — problema resolvido |
| Moveu parcialmente | Hipótese parcialmente validada — problema atenuado |
| Não moveu | Hipótese invalidada — problema persiste |
| Métrica não disponível | Lacuna de dado — avaliação qualitativa obrigatória |

Se a métrica não estava disponível (baseline não existia no briefing), o PM usa evidência qualitativa do CS como proxy — mas registra a limitação explicitamente.

---

### Pergunta 2 — O CS parou de receber sinais relacionados a esse problema?
*Dado qualitativo — padrão de atendimento.*

O CS é o termômetro mais rápido de produto da Zoppy. Se a feature funcionou, o volume de tickets sobre aquele problema cai. Se não mudou — o problema persiste, mesmo que a feature tenha sido entregue.

Perguntas para o CS:
- "Vocês ainda estão recebendo atendimentos sobre [problema]?"
- "Mudou alguma coisa desde o lançamento?"
- "O lojista ainda reclama de [comportamento específico]?"

---

### Pergunta 3 — O lojista consegue fazer o que não conseguia antes?
*Evidência comportamental — Clarity, dashboard, ou sessão direta.*

Essa é a pergunta mais importante — e a mais difícil de responder sem dado comportamental.

Fontes:
- **Clarity:** o comportamento de abandono sumiu? O lojista completa o fluxo agora?
- **Dashboard interno:** taxa de uso do módulo aumentou?
- **Sessão com lojista:** peça para um lojista realizar a tarefa que era problemática

Se nenhuma dessas fontes está disponível, registre como limitação e recomende configurar tracking antes do próximo lançamento.

---

## Os 4 resultados possíveis

### ✅ Hipótese validada
A métrica moveu, o CS sinalizou redução, o comportamento mudou. O problema foi resolvido.

**O que fazer:**
- Registre o aprendizado completo
- Documente o que funcionou — padrão replicável para problemas similares
- Feche o item no backlog como "resolvido"
- Sinalize para o time de design e engenharia — time que não vê resultado não aprende junto

---

### ⚠️ Hipótese parcialmente validada
A métrica moveu mas não atingiu a meta, ou moveu em algumas dimensões mas não em outras.

**O que fazer:**
- Identifique o que funcionou e o que não funcionou
- Documente a hipótese revisada: o que aprendemos que muda nossa próxima aposta?
- Decida: vale uma fase 2 para completar a solução, ou o problema restante tem prioridade menor agora?
- Registre a decisão com justificativa

---

### ❌ Hipótese invalidada
A métrica não moveu. O problema persiste.

**O que fazer:**
- Registre como "tentativa 1 — hipótese invalidada" com todo o contexto acumulado
- **Não descarte o problema** — descarte a hipótese. O problema pode continuar válido
- Volte para o discovery com mais inteligência: o que aprendemos que a tentativa 1 não sabia?
- O item volta para o backlog com status explícito e prioridade reavaliada pelo RICE

**O que não fazer:**
- Não tente justificar por que a métrica não se aplica mais
- Não mude a métrica retroativamente para o resultado parecer positivo
- Não ignore o resultado e avance para a próxima feature como se nada tivesse acontecido

---

### 🔍 Sem dado suficiente para avaliar
A métrica não estava disponível, o tracking não foi configurado, o prazo foi muito curto.

**O que fazer:**
- Registre a limitação com clareza
- Use evidência qualitativa como proxy temporário
- Estenda o prazo de avaliação por mais 2 semanas com tracking configurado
- Recomende ação corretiva para o próximo lançamento: *"antes de lançar, configurar evento X no Clarity"*

---

## O que o aprendizado alimenta

O ciclo fecha quando o aprendizado vira sinal para a Fase 1.

```
APRENDIZADO
        ↓
Hipótese validada → padrão documentado para reutilizar
Hipótese parcial → fase 2 entra como novo sinal de MELHORIA na Fase 1
Hipótese invalidada → problema volta para Fase 1 com contexto acumulado
Sem dado → recomendação de tracking entra como sinal de infraestrutura
```

**Todo aprendizado gera pelo menos um novo sinal.** Mesmo quando a hipótese é validada — o uso real do produto sempre revela algo que não estava no discovery.

---

## Compartilhamento com o time

O resultado de cada feature é visível para o time de design e engenharia — não fica só com o PM.

**Por quê:** time que não vê resultado não aprende junto. Designer que nunca sabe se o que desenhou funcionou não tem como melhorar. Engenheiro que não vê impacto do que construiu perde conexão com o problema.

**Como:** o PM compartilha o bloco de aprendizado na reunião de alinhamento semanal — não como relatório formal, mas como "fechamento de ciclo". 5 minutos, resultado da hipótese, o que aprendemos, o que muda.

---

## Formato do aprendizado

```markdown
# Aprendizado Pós-Lançamento — [Nome da feature]

**Data de avaliação:** [data]
**Prazo original:** [data que foi definida no briefing]
**PM responsável:** [nome]
**Categoria:** MELHORIA / FEATURE

---

## Referência

**Problema original:**
[Do briefing Bloco 2 — Jobs to be Done]

**Hipótese original:**
[Do briefing Bloco 4 — formato padrão]

**Métrica de sucesso:**
- Métrica: [do briefing Bloco 5]
- Baseline: [valor no momento do briefing]
- Meta: [valor que representava sucesso]

---

## Resultado

**Resultado da métrica:**
- Valor atual: [número]
- Variação: [% de mudança em relação ao baseline]
- Atingiu a meta? Sim / Parcialmente / Não / Sem dado

**Sinal do CS:**
[O CS parou de receber tickets sobre esse problema? O que mudou?]

**Evidência comportamental:**
[Clarity, dashboard, sessão com lojista — o que o dado mostra?]

---

## Classificação

**Resultado:** Hipótese validada / Parcialmente validada / Invalidada / Sem dado suficiente

**Posição na árvore de retenção:**
- Impacto observado em: Ativação / Engajamento / Expansão / Satisfação
- Impacto na retenção 90 dias: Positivo / Neutro / Negativo / Indefinido

---

## O que aprendemos

**O que funcionou:**
[O que confirmamos sobre o problema e a solução]

**O que não funcionou:**
[O que nossa hipótese errou]

**O que não sabíamos antes:**
[Descoberta nova que o uso real revelou]

**Hipótese revisada** (se aplicável):
[O que apostamos diferente na próxima rodada]

---

## Próximo passo

- [ ] Fechar item como resolvido
- [ ] Abrir fase 2 como novo sinal na Fase 1
- [ ] Retornar ao discovery com hipótese revisada
- [ ] Configurar tracking para próximo lançamento
- [ ] Compartilhar aprendizado com o time de design e engenharia

**Novo sinal gerado:**
[Descreva o sinal que esse aprendizado coloca de volta na Fase 1]
```

---

## Bloco de Status da Fase — formato obrigatório

```markdown
## Status da Fase — Aprendizado

- **Ciclo fechado?** Sim / Não / Parcialmente
- **Resultado da hipótese:** Validada / Parcialmente validada / Invalidada / Sem dado
- **Impacto na árvore de retenção:** Ativação / Engajamento / Expansão / Satisfação / Indefinido
- **Nível de confiança no resultado:** Baixo / Médio / Alto
- **O que foi aprendido:**
  - [principais descobertas em bullets]
- **Novo sinal gerado para Fase 1:**
  - [o que volta para o sistema de captura]
- **Ação recomendada:** Fechar / Fase 2 / Retornar ao discovery / Configurar tracking
- **Motivo:** [1-2 linhas]

---
🔄 Ciclo completo. Novo sinal alimenta: Fase 1 — Captura (zoppy-pm-capture)
📢 Compartilhar resultado com time de design e engenharia antes de fechar.
```

---

## Regras de comportamento

**Métrica definida antes — avaliada depois.** A métrica de sucesso não pode ser alterada depois do lançamento. Se o resultado foi ruim, o aprendizado é que a hipótese estava errada — não que a métrica estava errada.

**Hipótese invalidada não é fracasso.** É aprendizado. O problema volta para o backlog com mais contexto — não do zero. A equipe que invalida hipóteses rápido aprende mais rápido do que a equipe que nunca testa.

**Sem dado não significa sem avaliação.** Se o tracking não foi configurado, use evidência qualitativa como proxy. Registre a limitação e corrija para o próximo ciclo. Mas nunca pule a avaliação.

**Time vê o resultado.** O aprendizado não é propriedade do PM. Design e engenharia participaram da construção — participam do resultado. Ciclo fechado em público é o que cria cultura de produto.

**Todo ciclo gera sinal.** Mesmo hipótese validada gera aprendizado que alimenta a Fase 1. O produto que para de aprender começa a envelhecer.

**Prazo agendado no lançamento.** Se o PM não agendou a revisão no dia do lançamento, o ciclo vai morrer. Esse é o comportamento mais importante dessa fase — e o mais fácil de esquecer.
