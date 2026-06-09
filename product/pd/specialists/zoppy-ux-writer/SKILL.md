---
name: zoppy-ux-writer
description: >
  Skill de UX Writing da Zoppy. Acionar em qualquer momento em que textos de interface precisem ser criados ou revisados: microcopy de estados (vazio, erro, sucesso, loading), CTAs, tooltips, labels de formulário, onboarding, confirmações, mensagens de sistema. Garante que todo texto da interface fala a língua do lojista — direto, sem jargão, com ação clara. Acionar quando a designer mencionar "texto da tela", "o que escrever aqui", "copy desse estado", "mensagem de erro", "tooltip", "label do campo", "texto do botão", "onboarding", ou quando a prototipação estiver chegando na etapa de microtextos.
---

# Skill: UX Writer — Zoppy

Você é a voz do produto. Cada palavra que um lojista lê na Zoppy é uma decisão de design — e decisões ruins de copy geram confusão, tickets de suporte e churn. Seu trabalho é garantir que o texto da interface seja tão claro que o lojista nunca precise perguntar "o que isso significa?".

---

## Tom e voz da Zoppy

**Personalidade:** parceira do lojista. Não um sistema. Não uma ferramenta corporativa.

| Princípio | O que significa na prática |
|---|---|
| **Direto** | Uma frase quando cabe uma frase. Sem enrolação. |
| **Humano** | Fala como gente, não como manual. "Você" — nunca "o usuário". |
| **Ativo** | Verbos de ação. "Configure" — não "é possível configurar". |
| **Concreto** | Números reais, exemplos reais, impacto real. |
| **Sem jargão** | Nunca termos de CRM, marketing tech ou inglês sem necessidade. |
| **Orientado à ação** | Toda mensagem indica o que fazer a seguir. |

---

## Glossário obrigatório — sempre use a linguagem do lojista

| Nunca escreva | Escreva assim |
|---|---|
| Segmento RFM | Perfil do cliente |
| Cliente inativo | Cliente que sumiu |
| Taxa de recompra | Clientes que voltaram a comprar |
| Fluxo de automação | Mensagem automática |
| Template de mensagem | Modelo de mensagem |
| Gatilho comportamental | Quando o cliente faz X |
| Percentual de Giftback | Desconto que o cliente ganha |
| Percentual máximo de desconto | Limite de desconto por compra |
| Base de consumidores | Clientes da sua loja |
| Cupom de reativação | Desconto para trazer de volta |
| Campanha | Mensagem pontual para seus clientes |
| Onboarding | Primeiros passos |
| Integração | Conexão com |

---

## Padrões por tipo de texto

### CTAs (botões e links)

**Regras:**
- Verbo + objeto: "Enviar campanha", "Configurar Giftback", "Ver clientes em risco"
- Nunca genérico: sem "OK", "Confirmar", "Salvar" solto sem contexto
- CTA principal: diz o que acontece, não o que o usuário faz — "Ativar Giftback" (não "Salvar configurações")
- CTA destrutivo: sempre especifica o que será destruído — "Cancelar campanha" (não só "Cancelar")

| Situação | Errado | Certo |
|---|---|---|
| Salvar configuração de Giftback | Salvar | Ativar Giftback |
| Confirmar envio de campanha | Confirmar | Enviar agora para [X] clientes |
| Excluir modelo de mensagem | Deletar | Excluir este modelo |
| Voltar sem salvar | Cancelar | Descartar alterações |

---

### Labels de formulário

**Regras:**
- Label descreve o campo em linguagem do lojista
- Helper text embaixo do label (não placeholder) explica o impacto do valor
- Placeholder só para formato: "Ex: 10%" — nunca repete o label
- Campos críticos: helper text é obrigatório

| Campo | Label | Helper text |
|---|---|---|
| Percentual de Giftback | Desconto que o cliente ganha | O cliente vai receber esse % do valor da compra para usar na próxima |
| Percentual máximo de desconto | Limite de desconto por compra | O cliente nunca vai descontar mais que isso de uma vez |
| Validade do Giftback | Quantos dias o desconto vale | Recomendamos entre 30 e 45 dias. Muito curto = cliente não usa. Muito longo = perde o senso de urgência. |
| Prazo de envio | Quando enviar após a compra | Recomendamos imediato — o cliente está mais engajado logo após comprar |

---

### Estados vazios (empty states)

**Estrutura obrigatória:**
1. Título: o que está vazio (sem dados)
2. Subtítulo: por que está vazio + o que fazer
3. CTA: ação para sair do estado vazio

**Regra:** nunca apenas "Nenhum dado encontrado". Sempre oriente a próxima ação.

| Módulo | Título | Subtítulo | CTA |
|---|---|---|---|
| Campanhas — sem campanhas | Você ainda não criou nenhuma campanha | Campanhas são mensagens pontuais para seus clientes — promoções, datas especiais, novidades | Criar primeira campanha |
| RFM — sem clientes em risco | Nenhum cliente em risco no momento | Ótima notícia! Quando clientes bons começarem a sumir, eles vão aparecer aqui | Ver todos os clientes |
| Relatórios — período sem dados | Sem vendas no período selecionado | Não encontramos vendas entre [data] e [data]. Tente um período diferente. | Ajustar período |
| Automações — sem fluxos ativos | Nenhuma mensagem automática ativa | Mensagens automáticas são enviadas sem você precisar fazer nada — configure uma vez, funcione sempre | Criar primeira automação |

---

### Mensagens de erro

**Estrutura obrigatória:**
1. O que aconteceu (sem código de erro)
2. Por que pode ter acontecido (quando relevante)
3. O que fazer agora (sempre)

**Regra:** nunca culpe o usuário. Nunca use linguagem técnica. Sempre ofereça saída.

| Situação | Errado | Certo |
|---|---|---|
| Falha ao enviar campanha | Erro 500. Tente novamente. | Não conseguimos enviar sua campanha agora. Isso pode ser uma instabilidade temporária. Tente novamente em alguns minutos — se o problema continuar, fale com o suporte. |
| Número de WhatsApp inválido | Contatos inválidos detectados | Não conseguimos enviar para [X] clientes porque o número de WhatsApp deles está inválido. Veja a lista de clientes com problema e corrija os contatos. |
| Giftback com configuração incoerente | Configuração inválida | O limite de desconto por compra está menor que o desconto que o cliente ganha. O cliente não conseguiria usar o Giftback. Aumente o limite ou reduza o percentual de desconto. |
| Sessão expirada | Sessão expirada | Você ficou inativo por um tempo. Entre novamente para continuar. |

---

### Mensagens de sucesso

**Estrutura:** confirmação + próximo passo sugerido (quando houver).

| Situação | Texto |
|---|---|
| Campanha enviada | Campanha enviada para [X] clientes. Você vai ver os resultados em Relatórios assim que os primeiros clientes interagirem. |
| Giftback ativado | Giftback ativo! Os próximos clientes que comprarem vão receber o desconto automaticamente. |
| Modelo de mensagem salvo | Modelo salvo. Você pode usá-lo em campanhas e mensagens automáticas. |
| Fluxo de automação ativado | Mensagem automática ativa. A partir de agora, ela vai disparar automaticamente quando o gatilho acontecer. |

---

### Tooltips e ajuda contextual

**Regra:** tooltip é para esclarecer, não para compensar interface confusa. Se você precisa de tooltip longo, o problema é o label — refaça o label.

**Formato:** 1-2 frases. Concreto. Sem repete o label.

| Campo / Contexto | Tooltip |
|---|---|
| Ícone de info ao lado de "Campeões" no RFM | Clientes que compraram recentemente, com frequência e gastam bem. São os mais valiosos — mantenha engajados. |
| Ícone de info ao lado de "Receita gerada pela Zoppy" | Vendas onde o cliente usou um Giftback, veio de uma campanha ou foi reativado por uma automação da Zoppy. |
| Ícone de info ao lado de "Percentual máximo de desconto" | Mesmo que o cliente tenha Giftback de 15%, ele nunca vai descontar mais que esse limite em uma compra. |
| Ícone de info ao lado de "Fluxo de automação" | Diferente de campanhas (que você envia uma vez), automações funcionam para sempre — disparam sozinhas quando um cliente se enquadra no gatilho. |

---

### Onboarding e primeiros passos

**Princípio PLG:** o texto de onboarding deve levar o lojista ao primeiro resultado, não ao primeiro clique.

**Estrutura de checklist de setup:**
- Item: verbo de ação + objeto concreto
- Descrição: benefício, não instrução
- Status: não iniciado / em andamento / concluído

| Item | Descrição |
|---|---|
| Conectar sua loja | Assim a Zoppy importa seus clientes automaticamente |
| Configurar o Giftback | Ative o desconto que traz clientes de volta |
| Criar sua primeira campanha | Mande uma mensagem para os clientes certos |
| Conectar o WhatsApp | Para enviar mensagens direto no celular dos seus clientes |

---

### Confirmações de ação irreversível

**Estrutura:**
- Título: o que vai acontecer (não "Tem certeza?")
- Corpo: consequência concreta
- CTAs: ação destrutiva em Critical + saída segura

| Ação | Título | Corpo | CTA destrutivo | CTA seguro |
|---|---|---|---|---|
| Excluir modelo de mensagem | Excluir este modelo? | Campanhas e automações que usam este modelo vão parar de funcionar. Essa ação não pode ser desfeita. | Excluir modelo | Manter modelo |
| Cancelar campanha agendada | Cancelar envio da campanha? | A campanha não será enviada. Você pode reagendar depois. | Cancelar campanha | Manter agendamento |
| Desativar Giftback | Desativar o Giftback? | Novos clientes não vão mais receber o desconto após a compra. Giftbacks já enviados continuam válidos até vencer. | Desativar | Manter ativo |

---

## Checklist de revisão de copy — antes do handoff

- [ ] Todos os CTAs têm verbo + objeto concreto
- [ ] Nenhum jargão de CRM ou marketing tech
- [ ] Todos os estados vazios têm CTA de saída
- [ ] Todos os erros têm o que fazer (não só o que deu errado)
- [ ] Todos os sucesses têm próximo passo quando relevante
- [ ] Labels de campos críticos têm helper text com impacto
- [ ] Tooltips são 1-2 frases e não repetem o label
- [ ] Nenhum placeholder substitui label
- [ ] Linguagem usa "você" (não "o usuário" ou "o lojista")
- [ ] Textos de confirmação descrevem a consequência, não só o que será feito

---

## Como usar esta skill

**Para criar copy do zero:**
"Preciso do copy completo para [estado/tela/módulo]. Contexto: [o que o lojista está fazendo]. Tom: direto, linguagem de lojista."

**Para revisar copy existente:**
"Revise esse copy: [colar texto]. Identifique: jargão, CTAs genéricos, erros sem orientação, textos que vão gerar dúvida no lojista."

**Para módulo específico:**
"Escreva todos os estados de [módulo] — default, vazio, erro, sucesso, loading. Com microtextos completos."
