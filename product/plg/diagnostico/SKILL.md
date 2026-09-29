---
name: zoppy-plg-auditoria
description: >
  Testa um produto de ponta a ponta via Playwright como se fosse um usuario real (prioritariamente um non-client que chegou sozinho) e entrega um relatorio de quao PLG o produto esta, com achados priorizados e evidencias, pronto pra mandar pro time de produto.

  Acionar quando pedir "auditoria PLG", "testar o produto como cliente novo", "quao PLG esta [produto]", "medir TTV/aha moment", "onde o funil de self-service quebra", ou antes de propor solucao com zoppy-ux-plg.
---

# Skill: /plg — Auditoria PLG de Produto

## O que faz
Testa um produto de ponta a ponta via Playwright como se fosse um usuário real (prioritariamente um **non-client que chegou sozinho**) e entrega um relatório de quão PLG o produto está, com achados priorizados e evidências, pronto pra mandar pro time de produto.

## Uso
/plg [url do produto] [credenciais de teste, se o fluxo exigir]

## Régua (fonte única — NÃO duplicar aqui)
A definição do que é PLG vem do **playbook-produto §1 (Filosofia base)** — ler ANTES de começar o teste. Resumo: usuário resolve sozinho ponta a ponta; produto ensina inline; erro vira instrução acionável; defaults inteligentes + preview; tour guiado desde o dia 1; "chame o dev/admin" é anti-padrão. Se o playbook mudar, a régua desta skill muda junto — nunca editar a régua aqui.

O que ESTA skill adiciona por cima do playbook: o referencial Wes Bush, o funil de FORA pra dentro, a matriz de cenários, as personas e o formato do relatório.

## Referencial teórico (Wes Bush / ProductLed) — as lentes da auditoria
Base: **"Product-Led Growth"** (Wes Bush) e **"Product-Led Onboarding"** (Ramli John + Wes Bush). Cada framework vira pergunta de auditoria:

1. **Modelo de entrada (Free Trial vs Freemium vs Demo).** Qual é o modelo — e ele é deliberado? Produto que SÓ entra via demo/vendedor é sales-led por definição. Auditar: existe caminho free/trial? É opt-in (sem cartão) ou opt-out? Notion e Slack: freemium sem cartão, valor antes de qualquer conversa comercial.
2. **Value metric e pricing transparente.** O preço é público e cobrado numa métrica que cresce com o valor percebido (mensagens, conversas, receita gerada) — ou é "fale com vendas"? Contabilizei: calculadora de preço na home, o lead vê o número ANTES de se cadastrar. Slack: fair billing — só cobra quem usa. Pricing escondido = achado P0 numa tese PLG.
3. **Straight line to value (Product-Led Onboarding).** Traçar a linha reta entre o cadastro e o primeiro valor; TODO passo que não está nessa linha (CNPJ, cargo, telefone, tour forçado) é desvio — eliminar, adiar ou esconder. Auditar passo a passo: "este campo é necessário AGORA pra entregar valor?" Notion: você está editando um doc em segundos; template pronto = valor pré-fabricado antes de qualquer esforço.
4. **Value gap: valor percebido vs experimentado.** A promessa da landing (ex.: "seu agente que vende 24h") se cumpre na PRIMEIRA sessão? A distância entre o que a página vende e o que o onboarding entrega é o value gap — medir e nomear.
5. **Bowling Alley (os bumpers que impedem a bola de ir pra canaleta).** Dois trilhos: **product bumpers** (checklist de setup com progresso, tooltips contextuais, empty states que ensinam, celebração do primeiro sucesso) e **conversational bumpers** (e-mail/WhatsApp de ativação puxando de volta quem parou no meio). Auditar a existência dos dois — a maioria dos produtos só tem o primeiro, mal.
6. **Aha moment / magic number declarado.** O time sabe qual evento mensurável = usuário ativado? (Slack: ~2.000 mensagens trocadas.) Se o produto não empurra o usuário ativamente até esse evento, o onboarding não tem alvo. No relatório: qual seria o magic number do produto testado (ex.: "1ª venda fechada pelo agente") e quanto o fluxo atual aproxima o usuário dele.
7. **PQL (Product-Qualified Lead).** O uso gera sinal de qualificação (atingiu o aha, bateu no limite do free) pro comercial agir em cima — ou o funil PLG e o time de vendas nem se falam?
8. **Motor de crescimento no próprio uso.** O uso do produto expõe o produto a novos usuários? (Slack: convite de colega é o core loop; Notion: página pública com "made with Notion"; Dropbox: indicação premiada.) No Wpp Commerce, o análogo natural: o consumidor final que compra via agente é um lojista em potencial vendo o produto funcionar.

## A jornada auditada
| Estágio | Pergunta-chave | Métrica |
|---|---|---|
| 1. Descoberta | Um estranho acha o produto e entende a proposta em 30s? | clareza da promessa |
| 2. Entrada | Consegue criar conta sozinho, sem falar com humano? | existe self-signup? |
| 3. Setup | Conecta o que precisa (WhatsApp, catálogo, pagamento) guiado pelo produto? | passos até setup completo |
| 4. Aha moment | Quando ele VÊ o valor pela primeira vez? | **TTV: cliques e minutos até o primeiro valor** — medir de verdade, cronometrado |
| 5. Hábito | O produto puxa ele de volta e ensina o próximo passo? | empty states, nudges |
| 6. Expansão/Pagamento | Consegue fazer upgrade/pagar sozinho? | self-checkout existe? |

O relatório SEMPRE diz em qual estágio o funil quebra primeiro — esse é o achado nº 1.

## Personas de teste
1. **Non-client total** — chegou de anúncio/Google, não tem nada. É a persona prioritária.
2. **Cliente da base** — já tem conta/integração; mede fricção de adoção do produto novo.
3. **Usuário convidado** — recebeu link de alguém do time; o convite explica o contexto?
4. **Usuário que volta** — dia 2: lembra onde parou? O produto retoma?

## Matriz de cenários (o "teste TUDO" — rodar em cada tela/fluxo)
**Caminho feliz:** fluxo completo até o valor, cronometrado, contando cliques.
**Inputs:** submit vazio · e-mail/telefone/CNPJ inválidos · valores extremos (texto gigante, emoji, espaços) · copy-paste com espaço no fim · duplo clique no submit (cria duplicado?).
**Navegação:** voltar do browser no meio do fluxo · refresh no meio (perde o que digitou?) · deep-link em rota interna deslogado (volta pra onde depois do login?) · abrir em 2 abas · sessão expirada no meio de um form.
**Estados:** cada empty state (ensina ou é só vazio?) · loading (tem feedback ou congela?) · erro de rede (mensagem acionável?) · permissão negada (explica ou tela branca?).
**Ambiente:** viewport mobile (375px) · console do browser (erros JS?) · requests falhando (aba network) · lentidão simulada.
**Becos sem saída (caça ativa):** qualquer ponto onde a única saída implícita é "chamar alguém" — link de suporte como única ação, campo que só o admin preenche, integração sem instrução, erro sem próximo passo. Cada beco é um achado por definição.

## Conduta do teste (produção de verdade — cuidado)
Dados de teste sempre marcados: e-mail com +teste-plg, nomes "TESTE PLG".
**Nunca**: pagamento real, disparo de mensagem pra cliente real, exclusão de dado que não criei, ação em conta de cliente.
Screenshot de TODA evidência.
Se o produto tiver rate-limit/captcha, não tentar contornar — registrar como observação.

## Benchmark (pesquisar padrão de mercado antes de julgar)
**Onboarding zero-fricção**: Notion (template = valor pré-pronto), Canva (faz antes de cadastrar)
**Freemium + viral loop B2B**: Slack (convite de colega como core loop, fair billing)
**PLG em mercado "complexo/regulado" BR**: Contabilizei (calculadora de preço na home, abertura de CNPJ 100% self-service)
**Setup de integração técnica**: Shopify (checklist com progresso), Stripe (docs + test mode)
**Onboarding de WhatsApp API**: Wati/Zenvia (embedded signup da Meta)

O achado sai mais forte: "X quebra aqui; o padrão de mercado (empresa Y) é Z".

## Formato do relatório
1. **Veredito em 1 parágrafo** — quão PLG está, onde o funil quebra primeiro, e qual é o modelo de entrada hoje.
2. **Placar por estágio da jornada** — régua de 4 cores (verde/amarelo/laranja/vermelho) + placar das 8 lentes Wes Bush.
3. **TTV medido** — cliques e minutos até o primeiro valor (ou "∞") + value gap + magic number sugerido.
4. **Achados priorizados**: P0 (bloqueia o self-service) / P1 (fricção que derruba conversão) / P2 (polish). Cada achado: o que acontece + repro + screenshot + por que fere PLG + correção sugerida + benchmark.
5. **Lista de becos sem saída** — todos, mesmo os pequenos.
6. **O que já está bom** — pro time saber o que preservar.
