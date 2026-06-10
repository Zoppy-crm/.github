---
name: zoppy-plg-design
description: >
  Skill de PLG Design (Product-Led Growth) da Zoppy. Garante que cada tela facilita a ativação do lojista: aha moment definido, empty states com orientação ativa, onboarding progressivo, friction points identificados antes de prototipar. Acionar na ideação e prototipação de qualquer tela de configuração inicial, primeiro uso, empty state, checklist de setup, ou quando a tela precisa levar o lojista a um resultado sem ajuda humana. Acionar quando mencionar "primeiro acesso", "ativação", "onboarding", "lojista trava em", "não sabe o que fazer", "empty state", "zero state", "aha moment".
---

# Skill: PLG Design — Zoppy

O lojista precisa conseguir chegar ao primeiro resultado sozinho. Sem ligação de onboarding. Sem suporte. Sem manual. Se ele não consegue, o produto falhou — não ele.

---

## Aha moments por módulo

O aha moment é o instante em que o lojista entende, na prática, que a Zoppy vale o investimento. Cada módulo tem o seu — e cada tela deve facilitar chegar lá.

| Módulo | Aha moment | Como o design facilita |
|---|---|---|
| **Giftback** | Primeiro cupom resgatado pelo cliente | Preview do impacto antes de ativar. Confirmação ativa quando o primeiro Giftback for resgatado. |
| **Campanhas** | Primeira resposta de cliente após envio | Resultado em tempo real visível logo após envio. Sugestão de próxima campanha imediata. |
| **RFM** | Primeiro lojista que entende qual segmento agir agora | Cada perfil tem ação sugerida imediata. "Cliente que sumiu" — não "Em risco". |
| **Automações** | Primeira mensagem automática disparada sem intervenção | Confirmação ativa quando a primeira automação disparar. Status "funcionando" visível. |
| **Painel do Vendedor** | Primeiro contato feito pelo vendedor via painel | Tarefa de hoje sempre visível. Próxima ação sempre óbvia. |
| **Dashboard** | Primeiro mês com receita atribuída à Zoppy | "Receita gerada pela Zoppy" em destaque. Comparativo com mês anterior. |

---

## Framework de ativação por tela

Para cada tela em design, responda estas perguntas antes de prototipar:

**1. Qual é o resultado que o lojista precisa alcançar nesta tela?**
(não "o que ele pode fazer" — o que ele precisa conseguir)

**2. Qual é o menor número de passos para chegar lá?**
(cada passo a mais é uma oportunidade de desistência)

**3. O que pode travar o lojista nesta tela?**
(mapeie os friction points antes de criar a solução)

**4. Como a tela comunica que o lojista está no caminho certo?**
(progress, feedback, confirmações parciais)

**5. O que acontece quando a tela está vazia?**
(nunca mostrar vazio sem orientação. Sempre: o que fazer para ter dados aqui)

---

## Padrões de empty state com orientação ativa

Empty state não é "sem dados". É oportunidade de ativar.

### Estrutura obrigatória de empty state PLG:
1. **Ilustração** — comunica o estado sem texto
2. **Título** — o que ainda não existe (concreto, sem dramatizar)
3. **Subtítulo** — benefício de criar / configurar (o que o lojista ganha, não o que falta)
4. **CTA primário** — ação direta para sair do estado vazio
5. **CTA secundário** (opcional) — saber mais / ver exemplo

### Escala de orientação por módulo:

| Módulo | Nível de orientação necessário | Razão |
|---|---|---|
| Giftback — nunca configurado | **Alto** — guia passo a passo | Configuração errada gera prejuízo |
| Campanhas — sem campanhas | **Médio** — sugestão de primeira campanha | Baixo risco, alta motivação |
| Automações — sem fluxos | **Alto** — template pronto para ativar | Conceito não intuitivo |
| RFM — base importada mas sem segmentos | **Médio** — explica o que cada perfil significa | Dado é novo, linguagem estranha |
| Relatórios — sem dados no período | **Baixo** — só ajustar filtro | Problema é de filtro, não de ativação |

---

## Onboarding progressivo — padrões

O onboarding não é uma tela. É uma camada que aparece no contexto certo, no momento certo, e some quando não é mais necessária.

### Tipos de onboarding por contexto:

**Checklist de setup (primeiro acesso ao módulo)**
- Quando: lojista nunca configurou o módulo
- Formato: card colapsável com progresso (3/4 passos concluídos)
- Remove: quando todos os passos estão concluídos
- Nunca: obrigatório, bloqueante, sem como fechar

**Tooltip contextual (primeiro uso de feature complexa)**
- Quando: primeiro acesso a campo crítico (ex: percentual de Giftback)
- Formato: tooltip com exemplo de impacto real
- Remove: após lojista interagir com o campo uma vez
- Nunca: tooltips em sequência que parecem tour forçado

**Banner de resultado (após aha moment)**
- Quando: primeiro Giftback resgatado, primeira campanha respondida, primeira automação disparada
- Formato: banner de sucesso com o resultado + próximo passo sugerido
- Remove: após lojista clicar em "ver resultado" ou fechar

**Helper text inline (campos críticos permanentes)**
- Quando: campos onde erro = prejuízo (percentuais de Giftback, validade)
- Formato: texto fixo abaixo do label
- Remove: nunca — é informação estrutural

---

## Friction points mapeados por módulo

Identifique antes de prototipar. Para cada friction point, o design precisa de uma resposta.

### Giftback
| Friction point | Resposta de design |
|---|---|
| Lojista não entende a diferença entre os dois percentuais | Labels com impacto direto + preview calculado em tempo real |
| Lojista não sabe se o valor que colocou é "bom" | Benchmarks inline: "Lojistas semelhantes usam entre 5% e 12%" |
| Lojista não sabe quando o Giftback vai ser enviado | Timeline visual da jornada do cupom após a compra |
| Lojista não confia que o cliente vai usar | Dado de taxa de resgate de clientes similares (quando disponível) |

### Campanhas
| Friction point | Resposta de design |
|---|---|
| Lojista não sabe qual segmento escolher | Cada segmento mostra: quantos clientes + descrição em linguagem de lojista + sugestão de mensagem |
| Lojista escreve mensagem genérica | Exemplos de mensagem com bom desempenho inline, contador de caracteres, preview no celular |
| Lojista tem medo de enviar errado | Tela de revisão com resumo: X clientes, canal, mensagem, horário — antes do botão final |

### Automações
| Friction point | Resposta de design |
|---|---|
| Lojista não entende a diferença entre campanha e automação | Explicação visual: campanha = uma vez, automação = funciona sempre |
| Lojista não sabe o que vai disparar a automação | Timeline do gatilho com exemplo: "Quando um cliente não compra há 90 dias → recebe esta mensagem" |
| Lojista não sabe se está funcionando | Status em tempo real: "X mensagens enviadas este mês por esta automação" |

### WhatsApp API
| Friction point | Resposta de design |
|---|---|
| Processo burocrático fora do produto | Progress bar de etapas com o que está dentro vs. fora da Zoppy |
| Lojista não sabe o que acontece em cada etapa | Explicação do que acontece, quanto tempo leva, o que ele precisa fazer |
| Medo de errar e perder a conta | Alertas de prevenção antes das etapas críticas |

---

## Checklist PLG — antes de entregar para prototipação

Para cada tela nova ou reformulada:

- [ ] Aha moment do módulo está mapeado — a tela facilita chegar lá?
- [ ] Empty state tem CTA de saída + benefício (não só "sem dados")
- [ ] Campos críticos têm helper text com impacto real (não só formato)
- [ ] Friction points do módulo foram revisados — algum aparece nesta tela?
- [ ] Onboarding progressivo: aparece no momento certo, some depois
- [ ] Tela funciona sem onboarding (para lojistas que já passaram da fase de ativação)?
- [ ] Próxima ação sempre evidente — lojista nunca fica parado sem saber o que fazer
- [ ] Preview de impacto antes de ações configuráveis (Giftback, segmentação)

---

## Como usar esta skill

**Para nova tela de configuração:**
"Aplique o framework PLG para a tela de [configuração]. Mapeie: aha moment, friction points, empty state orientado, onboarding necessário."

**Para revisar tela existente:**
"Analise essa tela sob a lente PLG. O lojista consegue chegar ao resultado sem ajuda? Onde ele vai travar?"

**Para empty state:**
"Crie o empty state PLG para [módulo]. Inclua: estrutura completa, nível de orientação necessário, CTA de saída."
