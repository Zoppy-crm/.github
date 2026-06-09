---
name: zoppy-prototyping-figma
description: >
  Skill de Prototipação no Figma da Zoppy — sexta etapa da esteira. Produz spec completa (estados, microtextos, tokens, edge cases) e executa no Figma usando apenas componentes e tokens aprovados no DS Check. Herda toda a lógica de `zoppy-prototipacao` com bloco de Status da Etapa obrigatório e execução spec-driven: primeiro um plano de tarefas a partir da spec, depois execução de uma tarefa por vez, sempre com confirmação explícita da designer antes de avançar — nunca em lote, nunca apagando o que já existe. Acionar após DS Check concluído.
---

# Skill: Prototyping Figma — Zoppy

> Esta skill é a **Fase 6** da esteira de produto da Zoppy.
> Herda toda a lógica e formato da `zoppy-prototipacao` com os seguintes acréscimos:
> - Referência explícita ao DS Check (lista de componentes aprovados)
> - Bloco de Status da Etapa obrigatório ao final
> - Execução spec-driven: plano de tarefas → execução de uma tarefa por vez → confirmação da designer antes de cada avanço
> - Protocolo de verificação frame a frame

Leia e execute `zoppy-prototipacao` como base. Os acréscimos abaixo se sobrepõem onde houver conflito.

---

## Posição no fluxo

```
PM Intake → Briefing → Discovery → Ideação → DS Check → Prototyping ← VOCÊ ESTÁ AQUI → Handoff
```

**Entrada:** DS Check concluído (lista de componentes aprovados + tokens mapeados) + direção escolhida na ideação
**Saída:** spec completa + protótipo executado no Figma + checklist de edge cases + bloco de Status da Etapa

---

## Filosofia de execução

**Plano antes de pixels (spec-driven).** A execução acontece em dois tempos. Primeiro você transforma a spec num **plano de tarefas** ordenado e o submete para aprovação. Só depois de o plano ser aprovado é que você executa — e executa **uma tarefa por vez, parando para a confirmação da designer antes de cada avanço**. O plano é o contrato: nada vai pro Figma fora dele sem ser renegociado primeiro.

**Spec antes de pixels.** Nenhum frame no Figma antes de ter spec completa do que vai nesse frame: estados, microtextos, tokens, lógica condicional, edge cases. Criar sem spec é criar para refazer.

**Uma tarefa por vez, com confirmação.** Execute uma tarefa, verifique pelo protocolo frame a frame, mostre o resultado e **pare**. Só avance para a próxima depois de a designer confirmar explicitamente. Nunca execute duas ou mais tarefas em sequência sem confirmação no meio. Velocidade de execução no Figma é inversamente proporcional à qualidade.

**Nunca apague frames existentes.** Se algo precisa mudar, crie um frame novo ao lado. O histórico de versões importa — para o time, para o dev, para futuras iterações.

**Nunca use valor hardcoded.** Fill de cor via variável. Texto via text style. Padding via grid de 8px. Qualquer exceção precisa de justificativa explícita.

---

## Antes de executar no Figma

Verifique se o DS Check foi concluído:
- Há lista de componentes aprovados com keys?
- Há tokens de cor e text styles mapeados?
- Há lista de componentes proibidos?

Se não — sinalize: *"Prototipação sem DS Check executado. Recomendo executar `zoppy-design-system-figma` primeiro. Criar sem verificar o DS gera inconsistência e retrabalho na implementação."*

**Rastreamento com a esteira:** ao iniciar, referencie:
> "Prototipação iniciada com base na direção: [variante escolhida na ideação]. Componentes aprovados: [lista do DS Check]. Tokens: [lista]. Restrições: [componentes proibidos]."

---

## Protocolo de spec antes de executar

Para cada tela, produza a spec completa antes de abrir o Figma:

### Bloco de spec por tela

**Nome do frame:** [como vai se chamar na página WIP]
**Estado:** [Default / Loading / Erro / Vazio / Sucesso]
**Gatilho para este estado:** [o que faz aparecer]

**Hierarquia de conteúdo:**
1. [elemento no topo] — componente: [componente DS] — token: [token de cor] — text style: [style]
2. [segundo elemento] — ...

**Microtexto aprovado:**
- Título: "[texto exato]"
- Subtítulo / descrição: "[texto exato]"
- CTA: "[texto exato]"
- Empty state: "[texto exato]"
- Mensagem de erro: "[texto exato]"

**Lógica condicional:**
- Se [condição X] → [mostrar/esconder/mudar Y]

**Edge cases desta tela:**
- [situação] → [comportamento]

---

## Protocolo de verificação frame a frame

Antes de avançar para o próximo frame, verifique:

- [ ] Nome do frame está descritivo e segue o padrão (ex: "01 — Default", "02 — Erro de validação")
- [ ] Todos os fills são variáveis (não RGB hardcoded)
- [ ] Todos os text styles são do DS (não fontSize hardcoded)
- [ ] Todos os componentes são instâncias do DS (não criações locais)
- [ ] Padding segue o grid de 8px (não valores arbitrários)
- [ ] O texto do frame é real (não placeholder "Lorem ipsum" ou "[texto aqui]")
- [ ] O frame tem os dados corretos para o estado representado

Se qualquer item falhar — corrigir antes de avançar.

---

## Execução spec-driven

A execução tem **três fases obrigatórias e nesta ordem**: (1) Spec → (2) Plano de tarefas + aprovação → (3) Loop de execução tarefa a tarefa com confirmação. Nunca pule da spec direto para o Figma.

### Fase 1 — Spec

Produza o formato completo da `zoppy-prototipacao`:

1. Raciocínio inicial (referenciando o briefing + discovery + direção escolhida)
2. Spec completa: todos os estados por tela
3. Microtextos aprovados
4. Checklist de edge cases

Não abra o Figma ainda.

### Fase 2 — Plano de tarefas (antes de qualquer pixel)

Transforme a spec num **plano de tarefas ordenado**. Cada tarefa é a menor unidade executável e verificável de forma independente — em geral **um frame = um estado** (ex.: "Frame 02 — Empty state"). Ordene da fundação para o detalhe: estrutura/Default primeiro, depois os outros estados, depois variações de edge case.

**Formato do plano:**

```markdown
## Plano de execução — [Nome da Feature]

Página de destino: 🚧 WIP — [Nome da Feature]

- [ ] Tarefa 1 — Frame "01 — Default"
      Cobre: [estado/tela] · Componentes DS: [lista] · Tokens: [lista]
      Pronto quando: [critério verificável — passa no protocolo frame a frame]
- [ ] Tarefa 2 — Frame "02 — Empty state"
      ...
- [ ] Tarefa N — [ajuste/edge case]
      ...
```

Regras do plano:
- Uma tarefa nunca depende de algo que não esteja em uma tarefa anterior do mesmo plano.
- Toda tarefa referencia apenas componentes e tokens **aprovados no DS Check**. Se uma tarefa precisar de algo fora da lista aprovada, marque-a como **bloqueada** e sinalize antes de aprovar o plano.
- Se a spec cobre múltiplas telas/fluxos, o plano cobre uma de cada vez (segue o protocolo de múltiplos cenários da `zoppy-prototipacao`).

**Gate de aprovação do plano — pare aqui.** Ao apresentar o plano, finalize com:

> "Esse é o plano. Posso começar pela Tarefa 1, ou quer ajustar/reordenar algo antes? Não vou tocar no Figma até você aprovar."

Aguarde a resposta. Só prossiga para a Fase 3 após aprovação explícita. Se a designer pedir ajustes, atualize o plano e peça aprovação de novo.

### Fase 3 — Loop de execução (uma tarefa por vez, com confirmação)

Para **cada** tarefa, na ordem do plano:

1. **Anuncie** qual tarefa vai executar e o que ela cobre (uma linha).
2. **Execute apenas essa tarefa** no Figma (página `🚧 WIP — [Nome da Feature]`). Nada além do escopo da tarefa.
3. **Verifique** pelo `## Protocolo de verificação frame a frame`. Corrija o que falhar antes de mostrar.
4. **Mostre o resultado** — frame criado, o que foi feito, qualquer desvio do plano e o porquê.
5. **Pare e peça confirmação**, sempre encerrando com:

   > "Tarefa [N] concluída: [nome do frame]. Atualizo o plano para [N] ✓. Posso seguir para a Tarefa [N+1] — [nome], ou quer revisar/ajustar esta antes?"

6. **Aguarde.** Só execute a próxima tarefa após o "pode seguir" explícito da designer.

Regras inquebráveis do loop:
- **Nunca** execute duas tarefas sem uma confirmação entre elas — mesmo que pareçam triviais.
- **Nunca** apague frames de tarefas já concluídas. Mudança vira tarefa nova ao lado.
- Se durante a execução você descobrir que a tarefa precisa de algo fora do plano (componente não previsto, decisão de produto, microtexto faltando), **pare antes de improvisar**: descreva o que falta e pergunte como proceder. Spec-driven não admite decisão silenciosa no meio da execução.
- A cada tarefa concluída, reapresente o plano com o item marcado `[x]` para a designer acompanhar o progresso.

Quando todas as tarefas estiverem `[x]`, produza o **Bloco de Status da Etapa**.

---

## Bloco de Status da Etapa — obrigatório

```markdown
## Status da Etapa — Prototipação

- **Pode avançar?** [Sim / Não / Condicional]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi entregue:**
  - Frames criados: [lista com nome de cada frame]
  - Estados cobertos: [lista]
  - Microtextos aprovados: [Sim / Pendente revisão]
- **Hipóteses que ainda precisam ser validadas:**
  - [o que a prototipação revelou que precisa de validação — com lojista real ou com PM]
- **Lacunas abertas:**
  - [estados não prototipados por falta de informação]
  - [edge cases que precisam de decisão de produto antes de prototipar]
- **Recomendação:** [Pronto para handoff / Revisar com PM / Pausar — falta X]
- **Motivo:** [1-2 linhas]
```

**Critério para avançar para Handoff:**
- Todos os estados previstos no briefing estão prototipados
- Microtextos finais (não provisórios) em todos os frames
- Edge cases mapeados e com comportamento definido
- Nenhum componente hardcoded sem justificativa

---

## Contexto herdado

Herda todo o contexto de `zoppy-prototipacao`, `product-designer-zoppy`, `zoppy-figma-mcp` e `figma-use`.

**Ao concluir**, sinalize:
> "Prototipação concluída. Nível de confiança: [X]. Frames na página WIP. Próximo passo: aprovação do PM na WIP → `zoppy-handoff-builder` para documentação de engenharia."
