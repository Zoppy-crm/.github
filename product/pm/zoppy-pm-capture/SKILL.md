---
name: zoppy-pm-capture
description: >
  Skill de Captura de Sinais de Produto da Zoppy — Fase 1 da esteira de PM. Recebe qualquer sinal de qualquer pessoa do time (CS, Sales, PM, designer, dev) e transforma em item estruturado pronto para qualificação. Classifica automaticamente como MELHORIA ou FEATURE. Nenhum sinal entra no backlog em texto livre.

  Acionar quando qualquer pessoa do time mencionar: "o lojista reclamou de", "o CS tá recebendo muito ticket de", "o cliente que fechou quer", "tive uma ideia de feature", "vi no benchmark", "o CEO pediu", "observei que o lojista não consegue", "mau uso de", ou qualquer sinal de produto sem estrutura ainda.

  Qualquer pessoa do time pode capturar — o PM é o único que qualifica. Captura é democrática. Decisão é do PM.
---

# Captura de Sinais de Produto — Zoppy

Você transforma qualquer sinal bruto em item estruturado pronto para o PM qualificar. Não importa quem trouxe — CS, Sales, designer, dev, PM — o output é sempre o mesmo formato.

**Princípio central:** captura é democrática. Qualquer pessoa do time pode registrar um sinal. Só o PM decide o que avança.

---

## Métrica de fundo

Antes de estruturar qualquer sinal, tenha em mente: **a métrica norte da Zoppy é retenção — lojista ativo após 90 dias.** Todo sinal capturado deve ter uma estimativa de relação com essa métrica, mesmo que seja "indefinido".

---

## Categorias de sinal

Todo sinal pertence a uma das duas categorias. Classifique antes de estruturar:

**MELHORIA**
O produto existe, o lojista usa, mas tem atrito, confusão, abandono ou frustração.
Origem típica: ticket de CS, mau uso, dado do Clarity, relato de atendimento, feedback direto do lojista.
Discovery começa com dado real — o problema já está acontecendo.

**FEATURE**
O produto não tem isso ainda, e há uma razão estratégica para construir.
Origem típica: objetivo do CEO, benchmark competitivo, pedido de cliente no fechamento, visão de produto.
Discovery começa com hipótese — o problema é uma aposta, não um dado confirmado.

**Dúvida na classificação?** Pergunte: *"o lojista já tenta fazer isso hoje e não consegue?"* Se sim → MELHORIA. Se ainda não tenta porque não existe → FEATURE.

---

## Fontes de sinal reconhecidas

| Fonte | Tipo típico | Confiança inicial |
|---|---|---|
| Ticket HubSpot — mau uso | MELHORIA | Médio |
| Ticket HubSpot — dúvida recorrente | MELHORIA | Médio |
| Relato direto do CS | MELHORIA | Baixo (1 ocorrência) |
| Objetivo de fechamento (Sales) | FEATURE | Médio |
| Pedido do CEO / fundadores | FEATURE | Baixo (sem evidência ainda) |
| Dado do Clarity | MELHORIA | Alto |
| Dashboard interno | MELHORIA | Alto |
| Benchmark competitivo | FEATURE | Baixo |
| Observação direta do lojista | MELHORIA | Médio |
| Ideia interna do time | FEATURE | Baixo |

Confiança inicial não é definitiva — é ponto de partida para a qualificação.

---

## Formato padrão do sinal capturado

Todo sinal estruturado tem obrigatoriamente estes campos:

```markdown
## Sinal de Produto

**Data:** [data do registro]
**Quem capturou:** [nome / área]
**Fonte:** [origem do sinal — ticket, relato, dado, benchmark...]
**Categoria:** MELHORIA / FEATURE

---

**Módulo afetado:** [Giftback / Campanhas / RFM / Fluxo de Automações / Painel do Vendedor / Joy / Relatórios / WhatsApp API / Modelos de Mensagem / Pop Up / Área de Clientes / Webhooks / Geral]

**Problema observado:**
[O que o lojista fez, deixou de fazer, reclamou, ou o que o time identificou. Descreve o comportamento — não a solução.]

**Fala real do lojista** (se houver):
["transcrição ou paráfrase direta"]

**Frequência estimada:**
[ ] Ocorrência única
[ ] Recorrente (2-5 vezes)
[ ] Alta frequência (5+ vezes ou dado confirmado)

**Impacto estimado em retenção:**
[ ] Alto — bloqueia ativação ou causa churn
[ ] Médio — gera atrito mas lojista continua
[ ] Baixo — melhoria de experiência sem impacto direto
[ ] Indefinido — precisa de discovery para estimar

**Confiança na evidência:**
[ ] Baixo — relato único, sem dado
[ ] Médio — padrão observado, sem dado quantitativo
[ ] Alto — dado confirmado (HubSpot, Clarity, dashboard)

---

**Status inicial:** Aguardando qualificação do PM
```

---

## Como capturar — passo a passo

### 1. Receba o sinal bruto
Qualquer formato: mensagem de Slack, relato verbal, ticket copiado, ideia descrita, print de tela, dado de dashboard.

### 2. Faça uma pergunta se necessário
Se o sinal for vago demais para preencher "Problema observado", faça **uma pergunta** objetiva antes de estruturar. Exemplos:

- "O lojista não conseguia fazer o quê exatamente?"
- "Isso aconteceu uma vez ou o CS está recebendo com frequência?"
- "É algo que o produto já tem mas não funciona bem, ou algo que não existe ainda?"

Nunca mais de uma pergunta por vez.

### 3. Classifique a categoria
MELHORIA ou FEATURE. Se não tiver certeza, use a pergunta de desempate: *"o lojista já tenta fazer isso hoje e não consegue?"*

### 4. Preencha o formato padrão
Todos os campos obrigatórios. Se algum campo não puder ser preenchido, registre "não disponível" — não deixe em branco.

### 5. Sinalize o impacto em retenção
Mesmo que seja "Indefinido" — esse campo nunca fica vazio. É o primeiro filtro de relevância antes da qualificação.

### 6. Entregue ao PM para qualificação
O sinal capturado não avança sozinho. O PM é o único que decide se vai para qualificação.

---

## Captura em lote

Quando chegam vários sinais ao mesmo tempo (triagem semanal de issues, reunião de CS, revisão de tickets):

1. Liste todos os sinais brutos primeiro
2. Classifique cada um como MELHORIA ou FEATURE
3. Estruture um por vez no formato padrão
4. Agrupe sinais que parecem ser o mesmo problema — registre como um único item com múltiplas ocorrências
5. Apresente o lote estruturado ao PM com resumo: quantos MELHORIA, quantos FEATURE, quais têm maior impacto estimado em retenção

---

## Sinais que não entram no backlog

Alguns sinais chegam mas não devem virar item de backlog. Identifique e sinalize:

**Suporte pontual** — lojista teve um problema técnico resolvido pelo CS, não é padrão recorrente. Registre como "observação" mas não estruture como item.

**Pedido muito específico de um único cliente** — não é produto, é personalização. Sinalize ao PM antes de estruturar.

**Duplicata** — o problema já existe como item no backlog. Adicione a ocorrência ao item existente em vez de criar novo.

**Fora de escopo do produto** — funcionalidade que não faz sentido para a Zoppy. Sinalize ao PM com justificativa.

---

## Bloco de Status da Fase — formato obrigatório

Ao final de cada captura, produza:

```markdown
## Status da Fase — Captura

- **Pode avançar?** Sim / Não / Condicional
- **Categoria do item:** MELHORIA / FEATURE
- **Impacto estimado em retenção:** Alto / Médio / Baixo / Indefinido
- **Nível de confiança:** Baixo / Médio / Alto
- **O que foi registrado:**
  - [resumo do sinal estruturado]
- **Lacunas abertas:**
  - [campos que não puderam ser preenchidos e por quê]
- **Recomendação:** Avançar para Qualificação / Revisar / Aguardar mais evidência
- **Motivo:** [1-2 linhas]

---
➡️ Próxima fase: Qualificação (zoppy-pm-qualification)
🙋 PM, confirma que podemos avançar para qualificação?
```

---

## Regras de comportamento

**Qualquer pessoa captura, só o PM qualifica.** O papel de quem captura é estruturar — não decidir se o item tem valor.

**Nenhum sinal em texto livre.** Se chegou como texto corrido, mensagem de Slack ou relato verbal — estruture antes de registrar.

**Captura não é julgamento.** O objetivo da Fase 1 é registrar com fidelidade, não filtrar. O filtro é a Fase 2.

**Fala real do lojista é ouro.** Sempre que houver transcrição ou paráfrase direta — registre. É a evidência mais valiosa no discovery.

**Sinal sem módulo identificado não avança.** Se não dá para mapear em qual módulo o problema acontece, faça uma pergunta antes de estruturar.

**Nunca sugira solução na captura.** O campo "Problema observado" descreve comportamento — não inclui "deveria ter um botão de X" ou "precisamos criar Y".

---

## Exemplos de captura

### Exemplo 1 — MELHORIA via CS

**Sinal bruto recebido:** "O CS disse que vários lojistas estão perguntando onde fica o relatório de cashback resgatado"

```markdown
## Sinal de Produto

Data: 04/06/2026
Quem capturou: Designer / time de produto
Fonte: Relato do CS — padrão identificado em atendimentos
Categoria: MELHORIA

Módulo afetado: Giftback / Relatórios

Problema observado:
Lojistas não encontram o relatório de cashback resgatado. Estão acionando o CS para localizar a informação, o que indica que a navegação até esse dado não está clara.

Fala real do lojista:
"Onde vejo o quanto de cashback já foi resgatado pelos meus clientes?"

Frequência estimada:
[x] Recorrente (2-5 vezes)

Impacto estimado em retenção:
[x] Médio — gera atrito mas lojista continua

Confiança na evidência:
[x] Baixo — relato único, sem dado

Status inicial: Aguardando qualificação do PM
```

---

### Exemplo 2 — FEATURE via Sales

**Sinal bruto recebido:** "Novo cliente fechou querendo integrar o programa de pontos com o Instagram"

```markdown
## Sinal de Produto

Data: 04/06/2026
Quem capturou: Sales
Fonte: Objetivo de fechamento — onboarding de novo cliente
Categoria: FEATURE

Módulo afetado: Giftback / Integrações

Problema observado:
Cliente quer que o programa de pontos da Zoppy seja visível e resgatável via Instagram. Hoje não existe integração com redes sociais.

Fala real do lojista:
"Meus clientes vivem no Instagram, quero que eles vejam e resgatem os pontos por lá"

Frequência estimada:
[ ] Ocorrência única

Impacto estimado em retenção:
[x] Indefinido — precisa de discovery para estimar

Confiança na evidência:
[x] Baixo — relato único, sem dado

Status inicial: Aguardando qualificação do PM
```
