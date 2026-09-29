---
name: zoppy-growth-playbook
description: >
  Skill de Playbook de Growth da Zoppy. Documenta e aplica os processos internos consolidados da Zoppy — metodo BASE, segmentacao de clientes, ICP por produto, modelo de precificacao WPP Commerce, playbook de add-ons, e como o time de growth opera na pratica. E a memoria do time.

  Acionar quando o Growth precisar: aplicar um processo existente, documentar um processo novo, consultar como a Zoppy faz X, onboarding de alguem novo no processo, ou quando um experimento ganhou (Win) e precisa virar playbook.
---

# Playbook de Growth — Zoppy

Voce documenta e aplica os processos internos consolidados da Zoppy. E a memoria do time — o que ja foi aprendido, o que funciona, e como fazemos as coisas por aqui.

**Principio central:** processo que nao esta documentado nao existe para o proximo que chegar.

---

## Metodo BASE

O metodo BASE e o framework central de diagnostico e planejamento de campanhas da Zoppy. Aplicado pelo CS nas conversas com lojistas e pelo growth na definicao de estrategias de campanha.

### O que e

Framework de analise estrategica que permite identificar oportunidades dentro da base de clientes e transforma-las em campanhas e automacoes.

### As 4 letras

| Letra | Significado | Pergunta central |
|---|---|---|
| **B** | Business needs | Qual a alavanca comercial do mes? Onde esta a dor ou a meta? |
| **A** | Ativos | O que o marketing/comercial ja tem rodando que da pra amplificar pela Zoppy? |
| **S** | Sazonalidade | Qual gancho de calendario e relevante pra essa marca agora? |
| **E** | Experiencia | O que as campanhas e automacoes anteriores ja mostraram? O que otimizar? |

### Como usar nas conversas (CS)

1. **O metodo e invisivel** — nunca dizer "vou aplicar o metodo BASE". E so uma conversa natural.
2. **Ordem nas conversas iniciais:** B → A → S. O E entra mais fundo em clientes com historico.
3. **B e o ponto de partida** — antes de falar de sazonalidade, entender o momento comercial.

### Quando aplicar no growth

- Ao estruturar campanhas de reativacao para a base de lojistas
- Ao criar sugestoes de pauta para o grupo VIP
- Ao diagnosticar por que lojistas nao estao mandando campanhas

---

## Segmentacao de clientes Zoppy

### Tiers de plano

| Tier | Caracteristica | Comportamento tipico | Estrategia de growth |
|---|---|---|---|
| **Basico** | Plano entrada, menor ticket | Ativacao mais lenta, risco de churn, meta 45% de uso de campanhas | Onboarding intenso, primeiras campanhas guiadas |
| **Intermediario** | Plano medio | Engajamento medio, candidatos a expansao | Educacao sobre features nao usadas, add-on pitch |
| **Avancado** | Plano premium | Maior engajamento, base do add-on | Cases de sucesso, expansao WPP Commerce |

### Segmentacao por comportamento (para experimentos)

| Segmento | Criterio | Tamanho estimado | Estrategia |
|---|---|---|---|
| Nunca ativou campanha | 0 campanhas nos ultimos 90 dias | Alto (Basico principalmente) | Onboarding direto, BASE guiado |
| Ativou mas parou | 1+ campanha, inativo ha 30 dias | Medio | Reativacao via CS, sugestao de pauta |
| Engajado | Campanha nos ultimos 30 dias | Todos os tiers | Expansao, add-on |
| Em risco de churn | Queda de engajamento 30%+ em 60 dias | Variavel | Reignicao via WPP Commerce |
| Add-on prospect | Engajado + sem WPP Commerce | Intermediario/Avancado | Pitch consultivo |

### Segmentacao por tempo de vida

| Faixa | Prioridade | Intervencao tipica |
|---|---|---|
| 0-1 mes | Ativacao urgente | Onboarding guiado, primeira campanha |
| 1-3 meses | Formacao de habito | Check-in BASE, sugestao de pauta |
| 3-6 meses | Expansao ou estagnacao | Identificar feature nao usada |
| 6-12 meses | Expansao ou retencao | Add-on pitch, caso de sucesso |
| +12 meses | Case de sucesso ou churn silencioso | Revisao de saude, expansao |

---

## ICP por produto

### Como formalizar um ICP (metodo, use para qualquer produto)

Baseado em 4 fontes cruzadas (skill `defining-icp`/Lenny's, skill HubSpot ICP Builder, skill GitHub de 8 dimensoes, pratica de campo r/b2bmarketing) e validado pela primeira vez de ponta a ponta no WPP Commerce (26/08/2026, ver `outputs/growth/2026-08-26-icp-wpp-commerce-formalizado.md`).

**1. Nunca pare no firmografico.** Segmento/plataforma/faturamento e o que todo mundo tem — a camada que realmente prediz fit e a comportamental (gatilho: o que muda AGORA pra essa loja procurar solucao) e a emocional/JTBD (a dor real, na fala do lojista, nao em adjetivo de marketing). Se o ICP so tem firmografico, ele esta incompleto, nao pronto.

**2. Green / Yellow / Red, sempre os 3 — nao so "ideal vs. problematico".**
- 🟢 Green: bate todos os criterios — prospeccao ativa em todos os canais.
- 🟡 Yellow: bate parte dos criterios ou tem sinal forte fora do padrao (ex: cliente real que quebra uma regra do ICP mas converteu mesmo assim) — so engajar se vier inbound, nunca prospectar a frio.
- 🔴 Red: exclusao explicita, mesmo pra conta grande. **Um ICP sem Red e so uma lista de desejos.**

**3. Gatilho de compra != dor generica.** "Loja que quer vender mais" nao e gatilho — e generico demais pra qualquer loja. O gatilho tem que ser algo que muda de estado (estourou o limite do plano, comecou a receber X conversas/mes, comprou um produto complementar). Prefira sinal comportamental de uso real (dado que a Zoppy ja tem) a proxy indireto (faturamento, porte).

**4. Reachability e pre-requisito, nao detalhe.** Um segmento que so foi validado por um canal manual e nao-escalavel (ex: WhatsApp pessoal de uma pessoa) nao e ICP fechado — e uma hipotese validada em um canal so. Declarar isso explicitamente.

**5. Declare os gaps, nao esconda atras de confianca falsa.** Todo ICP formalizado tem que listar o que ainda e suposicao (persona formal, motivo de recusa dos que nao compraram, teste de periferia) — nao preencher com dado inventado so pra parecer completo.

### Zoppy Core (campanhas + automacoes)

**ICP ideal:**
- Loja de varejo (moda, beleza, casa, infantil)
- Base de clientes ativa (500+ contatos)
- Ja tem WhatsApp Business configurado
- Tem time de marketing ou dono que faz marketing
- Busca recompra e relacionamento com base

**ICP problemático (risco de churn):**
- Loja sem base de contatos (< 100 clientes)
- Sem habito de comunicacao com clientes
- Expectativa de leads novos (nao e o produto)

> Nao formalizado com o metodo acima ainda (sem Green/Yellow/Red, sem gatilho comportamental testado contra dado real). Candidato a proxima aplicacao do metodo.

### WPP Commerce (IA de vendas no WhatsApp)

**Formalizado com o metodo completo em 26/08/2026** — ver `outputs/growth/2026-08-26-icp-wpp-commerce-formalizado.md` para o documento inteiro (dor/JTBD vetados por battlecard, funil de conversao real, sinais de intencao de compra, 6 gaps explicitos). Resumo operacional:

**🟢 Green (prospeccao ativa):**
- Segmento moda/cosmeticos/joias/calcados **E**
- Plataforma Shopify, NuvemShop, Tray ou VTEX **E**
- Volume de conversas/mes no percentil ≥50% dentro do proprio plano (Basico≥36, Intermediario≥74, Avancado≥138) — sinal direto de que a dor ja esta acontecendo, mais forte que faturamento ou pedidos

**🟡 Yellow (so engajar se vier inbound):**
- Bate 2 dos 3 criterios acima — ex: fatura bem mas fora do segmento moda, ou plataforma fora da lista com sinal forte de dor (caso real: Anjuss, maior comprador, usa wake-commerce — nao VTEX)

**🔴 Red (nao prospectar, mesmo conta grande):**
- Plataforma fora de Shopify/NuvemShop/Tray/VTEX e sem integracao de e-commerce nenhuma (produto nao funciona sem catalogo pra indexar)
- Conversas/mes abaixo do percentil 50 do proprio plano (sem sinal de dor)
- WooCommerce/Magento (em avaliacao, ainda nao suportado)

**Erros ja testados e descartados** (nao repetir): faturamento R$50k+ sozinho exclui 17% dos compradores reais; segmento sozinho e sinal fraco (lift 1,3x); plataforma isolada sem o resto exclui o maior comprador real.

**Gap mais serio:** o funil que validou esse ICP (300 contatados → 40 responderam → 13 fecharam) rodou quase 100% por um canal manual e nao-escalavel. Tratar esse ICP como validado no sinal, nao validado no canal de aquisicao.

### Add-on geral (mensagens extras)

**ICP ideal:**
- Lojistas que estao estourando a franquia regularmente (2+ meses)
- Lojistas com campanhas de alto volume (liquidacoes, lancamentos)
- Intermediario/Avancado engajados

> Nao formalizado com o metodo acima ainda.

---

## Modelo de precificacao WPP Commerce

### Principio de precificacao

Cobramos por **conversa finalizada**, nao por mensagem enviada. Isso alinha o incentivo: a Zoppy so ganha quando o lojista tambem ganha (a conversa chegou ao fim — vendeu, resolveu, converteu).

### Por que conversa e nao mensagem

- Mensagem e puro volume — nao reflete resultado
- Conversa captura a jornada completa do cliente
- Mais defensavel comercialmente ("voce paga pelo que funciona")
- Alinha com a visao do P3: vender resultado, nao mensageria

### Estrutura de tiers (referencia)

Tiers por volume de conversas/mes — com margem para ajuste conforme validacao com clientes.

---

## Playbook de add-ons (canais de ativacao)

### Tier 1 — Canais de baixo esforco e alta escala

- **Pop-up in-app:** ativado por comportamento (lojista estourou franquia, lojista em plano elegivel)
- **Banner na plataforma:** visibilidade permanente para elegíveis
- **PQL triggers:** automacao baseada em comportamento que indica readiness

### Tier 2 — Canais de medio esforco

- **Email de dor:** para lojistas que estouraram franquia mas nao converteram no in-app
- **Live de produto:** para base engajada, combina educacao e oferta
- **Grupo VIP:** mensagens segmentadas para base com relacionamento ativo

### Tier 3 — Canais de alto esforco e alta conversao

- **Mensagem 1:1 personalizada:** para lojistas de alto potencial (upgrade recente, multiplos estouros)
- **Outreach via CS:** early adopters identificados pelo CS com relacionamento forte
- **Cold call:** para base quente que nao respondeu outros canais

---

## Como documentar um novo playbook (pos-Win)

Quando um experimento e declarado Win, documentar aqui:

```markdown
### Playbook — [Nome do experimento]

**Data de validacao:** [data]
**KR que move:** [KR associado]
**ICE Score original:** [score]

**O que foi testado:**
[Descricao do mecanismo]

**Para qual publico:**
[Segmento especifico]

**Resultado obtido:**
[Metrica + magnitude]

**Como reproduzir:**
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

**Quem pode executar:** [Growth / CS / automatizado]

**Restricoes e cuidados:**
[O que nao fazer, riscos identificados]
```

---

## Regras de comportamento

**Playbook sem resultado nao e playbook — e processo.** So documenta como playbook o que foi validado por experimento.

**O metodo BASE e invisivel nas conversas com lojistas.** Nunca nomear o framework — aplicar naturalmente.

**ICP problemático e tao importante quanto ICP ideal.** Saber para quem NAO vender evita churn antecipavel.

**Green/Yellow/Red, nao so ideal/problematico, quando formalizar um ICP do zero.** O Yellow existe porque nem todo caso real cabe limpo em "sim" ou "nao" — forcar binario perde sinal (ex: o maior comprador do WPP Commerce quebra o criterio de plataforma). E todo ICP formalizado declara os gaps abertamente em vez de preencher com suposicao disfarcada de dado.

**Todo Win vira playbook.** Aprendizado que nao e documentado nao existe para o proximo ciclo.
