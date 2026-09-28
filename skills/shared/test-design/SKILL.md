---
name: test-design
description: Use when writing, adding or changing tests or spec files during development — a feature, a bugfix, "escreve o teste", "cria o spec", "adiciona teste pra isso", "cobre com teste", "write tests for", "add tests", "test this service", "TDD", "red-green", ".spec.ts", "test coverage" — and before opening a PR that changes tested behavior.
---

# Test design

## Princípio

Um teste existe para **tentar quebrar o código**, não para confirmar o que ele já faz. Por isso o esperado de cada teste vem da **regra**: card, critério de aceite, contrato de quem chama. Nunca da leitura da implementação.

Se a regra não diz como o sistema deve se comportar numa situação, isso não é um detalhe para preencher com o que o código faz hoje. É uma **pergunta para o dev**, e ela vem antes do teste.

**As duas regras que não têm exceção:**
1. Não escreva um esperado que você só conhece porque leu o código.
2. Não mude um esperado para o teste passar. Teste que falha contra o código é um achado, não um erro do teste.

## Procedimento

### 1. Leia a regra antes do código

Procure, nesta ordem: a tabela "Exemplos" dos critérios de aceite do card; o resto do card ou do refinamento; o concept OKF da feature; o contrato de quem chama (outro serviço, o nó do workflow, a tela). Anote o que cada fonte diz. Só depois leia a implementação.

### 2. Liste as classes de cada entrada

Para cada coisa que a função recebe ou lê (parâmetros, campos do payload inclusive os opcionais, sessão, estado prévio no banco, quantas vezes roda, ambiente), liste as classes de equivalência e os limites. Use o [catalogo-de-entradas.md](catalogo-de-entradas.md). Em todo limite numérico ou de data: o valor exato, um abaixo, um acima. Para helper, normalizador ou mapper, some a skill `property-tests`.

### 3. Decida o esperado de cada classe: pergunte o que importa, declare o resto

Para cada linha, o esperado e a fonte dele. Quando nenhuma fonte responde, a linha é **pergunta** ou **suposição**. O dev responde poucas perguntas com atenção e ignora uma lista longa, então separe:

**Pergunta** é a linha em que o comportamento atual do código é **suspeito**:
1. o código contradiz outra fonte (quem chama, o outro sistema, o concept, o nome do método);
2. o código trata uma classe **em silêncio**: descarta, usa default, trata vazio ou `0` como ausente, engole erro;
3. há um limite (número, data, quantidade) sem regra que diga de que lado ele fica;
4. a regra vale para uma variante (método, provedor, role, status) e não se sabe se vale para as outras.

**No máximo 5 perguntas por arquivo**, na ordem acima. Cada uma diz o que o código faz, por que é suspeito e qual teste depende da resposta:

> **E4 — cupom de R$1.** O código recusa (`amount <= 1`). O nó de cupom do workflow aceita R$1. Qual é o certo? Se for "aceita", o teste E4 vai falhar contra o código atual.

**Suposição** é o resto: a linha sem regra em que o código faz algo razoável. Não pergunte. Escreva o teste com o comportamento atual, marque a fonte como `suposição` e liste todas num bloco só, para o dev corrigir se quiser:

> Vou assumir, salvo correção: E9 lista vazia devolve `[]`; E11 telefone sem DDI é aceito; E14 …

**Nunca pergunte** sobre a mecânica do teste (mockar ou não, qual helper, adicionar dependência): decida pelas convenções do projeto. Nem sobre detalhe interno que nenhum chamador enxerga.

A resposta de cada pergunta vira a fonte da linha (`dev, <data>`).

### 4. Escreva e rode os testes

Um `it()` por linha que o teste unitário cobre, com o ID no começo do nome: `it('E4 cupom de R$1 é válido')`. Cada teste monta a fixture **com o valor da linha** e verifica **o esperado exato**. Evite os vícios de [vicios-de-spec.md](vicios-de-spec.md). Convenções de setup do backend em [convencoes-nest.md](convencoes-nest.md).

Rode só o spec do arquivo. Quando um teste falhar:

> **E4 falhou.** Esperado (dev, 26/09): cupom de R$1 válido. O código recusa em `create-provider-coupon.helper.ts:88`. É bug no código, ou a regra é outra?

**Pare e mostre ao dev.** Não altere o esperado nem o código sem a decisão dele.

## Saída no PR

```markdown
## Entradas testadas
| ID | Entrada | Esperado | De onde veio | Coberto por |
|----|---------|----------|--------------|-------------|

## Perguntas feitas
- E4: cupom de R$1 → válido (dev, 26/09)

## Suposições
- E9, E11, E14 (comportamento atual; corrija se estiver errado)

## Achados
Bugs pegos na criação dos testes: 1
- E7: <o que era esperado × o que o código fazia> → bug, corrigido neste PR
- E9: <o que era esperado × o que o código fazia> → regra era outra, teste ajustado (não conta)
```

"Coberto por" é `unit`, `QA` (vira caso de QA pela `return-solution`) ou `não coberto: <motivo>`.

**A linha "Bugs pegos na criação dos testes: N" é obrigatória**, com esse texto exato, mesmo quando N é 0. Ela é contada automaticamente nos PRs, e o PR com 0 também entra na conta, como denominador. Conta como bug pego o teste que falhou contra o código, que o dev confirmou ser bug, e que teve o código corrigido. Não conta quando o dev decidiu que a regra era outra e o teste foi ajustado; esse achado fica listado, marcado "não conta".

## Bugfix

A linha E1 é a entrada que quebrou, e o teste dela **falha antes do fix**. Rode-o antes de corrigir e confirme. Depois passe pelas classes vizinhas da mesma dimensão, porque o bug costuma ter irmãos.

## Sinais de que você está fazendo o teste passar

| Pensamento | O que fazer |
|---|---|
| "O código faz X, então o esperado é X" | De onde vem X além do código? Se de lugar nenhum, pergunte |
| "O card não fala disso, mas é óbvio" | Se o código trata em silêncio ou contradiz alguém, pergunte. Se não, declare como suposição |
| "Vou perguntar tudo que não sei" | Até 5 perguntas, as suspeitas. O resto vira suposição declarada |
| "O teste falhou, vou ajustar o valor esperado" | É um achado. Mostre ao dev |
| "Esse caso de borda é improvável" | Pergunte se é impossível. Improvável acontece em produção |
| "Vou testar só o caminho feliz e o do bug" | Passe por todas as dimensões do catálogo que o código lê |
| "Uso o valor padrão da factory, funciona" | O valor da linha é o ponto do teste |
