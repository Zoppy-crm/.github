---
name: severidade-bugs
description: Classifica a severidade de qualquer bug da Zoppy (Baixo P3, Médio P2, Alto P1, Crítico P0, Catastrófico) pelo Playbook de Severidade, a régua única da empresa, e devolve nível, gravidade, alcance, justificativa, exemplo real parecido, confiança e o SLA do card (de cliente ou interno). É a fonte oficial da régua desde 10/10/2026 e aplica direto, sem gate, exceto Catastrófico (para e avisa) e Crítico (aplica e destaca). Use SEMPRE que alguém for criar um card de bug, em especial card de bug interno ("cria um card de bug interno", "abre um bug interno", "registra esse bug", "abre card desse defeito que achei"): a `flow-bug-card` chama esta skill antes de criar o card, para já sair com Severity, Priority e SLA preenchidos. Use também quando pedirem "qual a severidade desse bug", "classifica a severidade", "é P1 ou P2?", "reclassifica a severity", "esse card está com a severidade certa?", "severidade desse ticket", "pontua esse bug", "isso é crítico?", "abre war room?", "qual o SLA desse bug?", "qual o prazo de um card interno P1?", ou quando outra skill precisar de severidade (pipe do suporte em N3, cards dos Detetives, medição de concordância, weeklies de bugs). Também responde dúvida de regra ("IA do WhatsApp Commerce é Alto?", "integração numa empresa só é Médio?").
---

# Severidade de bugs da Zoppy

Uma régua só pra toda a Zoppy, venha o bug do suporte, de um Detetive, de um alerta ou de um dev que achou o defeito trabalhando. Esta skill é a fonte oficial desde 10/10/2026 (decisão do Solon, Supervisão de Suporte Técnico, depois do teste em produção de 08 a 10/10).

**Fonte da regra:** `playbook.md`, nesta mesma pasta (`.claude/skills/severidade-bugs/playbook.md` no repo), versão vigente v0.7. Leia o arquivo inteiro na primeira classificação da conversa; este SKILL.md resume o procedimento, não substitui o playbook.

**Onde a régua muda:** só por PR no `Zoppy-crm/.github` (`skills/shared/severidade-bugs/`), com aprovação do dono da régua (Solon). A cópia em `.claude/skills/` de cada repo é gerada pelo Sync Skills e não se edita à mão. O Google Doc "Playbook de Severidade de Bugs Zoppy" é espelho: quem muda a regra atualiza o doc no mesmo PR.

**Escrita:** sem travessão em nenhum texto gerado (nem "—" nem "--").

## Quando aplicar sem perguntar

| Nível | O que fazer |
|---|---|
| Baixo, Médio, Alto | Aplica direto, inclusive com confiança baixa. Registra a dúvida quando houver. |
| Crítico | Aplica e destaca no topo da resposta (é raro: 6 em uns 200 bugs desde 02/09). |
| Catastrófico | **Para e avisa** quem pediu, com o bug, o que está fora e a evidência: o Solon precisa saber na hora, e a Sala de Guerra é decisão dele. Enquanto isso, grava CATASTRÓFICO na Severity do card (ou Crítico no campo do HubSpot, que não tem Catastrófico), pra não ficar sem nível. |

Quem chama a skill decide onde gravar (tabela "Onde a severidade vai"). Esta skill classifica, calcula o SLA e diz o destino.

## Algoritmo (seção 6 do playbook, sempre nessa ordem)

**1. É bug?** Bug é quando o sistema não faz o que a regra atual de produto manda. Não pontua: mal uso, dúvida, configuração inicial, melhoria, solicitação de dados, instabilidade de terceiro tratada corretamente, dado errado na origem, duplicado ("Duplicado do #número"), teste interno. Terceiro que falha e a Zoppy esconde (perde dado, mostra sucesso falso) é bug na parte da Zoppy. Não use a `categoria_do_ticket` do HubSpot como prova: vale o conteúdo.

**2. Gatilho Catastrófico?** Plataforma ou módulo central fora pra base inteira; acesso entre empresas explorado ou dado de uma empresa aparecendo pra outra; perda ou corrupção em massa com efeito real. Card retroativo de incidente resolvido herda o nível mas não abre Sala de Guerra.

**3. Teste do Crítico:** os três ao mesmo tempo e confirmados na evidência: fluxo inteiro (todas as empresas de um gateway, provedor ou funcionalidade), sem contorno pro cliente, dinheiro ou segurança. Faltou um, segue.

**4. Funções sempre Alto**, mesmo numa empresa só:
- Integração com entrada de dados (pedido, cliente, cupom, produto, status, devolução) que não entra, entra errado, duplica ou é descartada. Exceções: campo personalizado só é Alto se alimenta fluxo, segmento ou mensagem ativos (sem conseguir verificar, Médio e registre a pergunta); dado errado na origem não é bug; integração que só atrasa segue a matriz.
- Automação que deixa de rodar (fluxo que não dispara, etapa que falha, gatilho que perde configuração, tarefa não criada). Só atrasar não entra.
- Cobrança, upsell ou fatura da Zoppy cobrando errado ou sem entregar o contratado. Cobrança não emitida: Médio pontual, Alto sistêmica.
- Acesso indevido dentro da mesma empresa.
- **IA do WhatsApp Commerce não entra aqui:** é Médio (P2) com Priority P1 sugerida, a não ser que passe nos passos 2 ou 3.

**5. Gravidade × alcance** pro resto:

| | A1 Pontual | A2 Sistêmico (confirmado) |
|---|---|---|
| G1 visual, texto, centavo | Baixo | Baixo |
| G2 funcional com contorno, exibição errada | Médio | Alto se afeta decisão do cliente (segmento, receita), senão Médio |
| G3 função parada ou dado, dinheiro, conteúdo errado | Médio, ou Alto se a função central está parada pra empresa | Alto |

Alcance potencial (depende de condição incomum) conta como pontual. Outra empresa citada no título sem evidência no corpo continua pontual. Contorno que só o time interno faz (script, Swagger, banco) conta como sem contorno.

**6. Conferir com os exemplos reais** da seção 5 do playbook. Na dúvida entre dois níveis, o menor, e registre a dúvida com os dois níveis.

## Card de bug interno

Card interno é o bug achado **antes do cliente**: dev trabalhando, QA, monitoramento, alerta, Detetive, revisão. No `bug-report.yml` é o card com "Relatado por cliente?" desmarcado e sem a label `client:report`.

O que muda em relação ao card de cliente:

- **Alcance vem da causa raiz e da evidência**, não de relato. Se o dev sabe que o defeito acontece no uso normal pra toda empresa que usa a função (leu o código, viu o log), é A2. Se depende de condição incomum, é A1. "Pode acontecer com qualquer um" sem evidência é potencial, logo A1.
- **O prazo é o dobro do de cliente** (tabela "Prazo e SLA").
- **Sem relato, a confiança costuma ser média ou baixa.** Isso não trava a aplicação: aplica e registra a dúvida.
- **Pergunte o mínimo.** Antes de classificar, só pergunte o que muda o nível e não dá pra tirar do contexto ou do código: o dado errado chega ao consumidor? tem contorno pro lojista? acontece pra toda empresa que usa a função? Uma rodada de perguntas no máximo; o resto vira `perguntas_pendentes`.
- **Priority:** card interno não tem contexto comercial (HighTouch, contrato, reincidência de cliente), então a Priority sugerida é igual à Severity, com uma exceção: IA do WhatsApp Commerce sai com Priority P1. Se quem pediu trouxer contexto (cliente grande esperando, incidente recorrente), a Priority sobe, a Severity não.

## Melhoria

Não pontua nas métricas de bug, mas recebe severidade **com olhar de melhoria**: mesma matriz aplicada ao estrago que a regra atual causa (perder venda ou decidir errado pesa mais que incômodo). Crítico e Catastrófico não se aplicam. Diga sempre "severidade de melhoria". Solicitação de dados (exclusão, alteração) não recebe severidade. Se quem pediu um card de bug descreveu uma melhoria, avise e sugira `flow-refinement`.

## Erros proibidos (seção 8)

1. HighTouch, tamanho do cliente ou tom do relato mudando severidade (isso é Priority).
2. Crítico pra dado ou conteúdo errado numa empresa só.
3. Crítico sem os três critérios confirmados.
4. Outra empresa no título tratada como sistêmico sem evidência.
5. Alcance potencial tratado como sistêmico.
6. Subir por reincidência.
7. Pontuar terceiro quando a Zoppy tratou bem a falha.
8. Médio pra integração com entrada de dados (fora as exceções).
9. Justificativa citando outro ticket ou card (cada caso só pelo próprio mérito).
10. Alto pra IA do WhatsApp Commerce só por ser a IA.

## Saída

Por bug: nível, GitHub Severity (P3, P2, P1, P0, CATASTRÓFICO), pontos (1, 2, 4, 8, 16), gravidade, alcance, função sempre Alto (se for), teste do Crítico (três booleanos), justificativa de 2 a 4 frases só com fatos deste caso, exemplo real mais parecido do playbook, confiança, pergunta pendente, Priority sugerida, **tipo de card (cliente ou interno) e data do SLA**, e ponto em observação da seção 10, quando tocar. Formato JSON completo na seção 9 do playbook, acrescido de `"tipo_card": "cliente | interno"` e `"sla": "YYYY-MM-DD | null"`.

Na conversa, mostre um resumo curto antes do JSON:

```
Severidade: Médio (P2) · G3, A1 · confiança média
Priority: P2 · SLA interno: 05/11/2026 (6ª janela de deploy)
Por quê: <2 a 4 frases>
Exemplo parecido: #12010
Dúvida: <se houver>
```

## Prazo e SLA (seção 5 do playbook)

**O SLA do card sai da Priority, não da Severity.** As duas usam a mesma escala; quando divergem (HighTouch, reincidência, IA do WhatsApp Commerce), o prazo é o da Priority. Ex.: Severity P2 com Priority P1 num card de cliente dá SLA de 2 janelas.

| Priority | Card de cliente | Card interno (o dobro) |
|---|---|---|
| Baixo P3 | sem prazo travado | sem prazo, revisão em 30 dias corridos |
| Médio P2 | 3 janelas de deploy (ter/qui) | 6 janelas (cerca de 3 semanas) |
| Alto P1 | 2 janelas | 4 janelas (cerca de 2 semanas) |
| Crítico P0 | 2 dias corridos | 4 dias corridos |
| Catastrófico | imediato, Sala de Guerra | igual |

Janelas contam a partir do dia seguinte à criação. Card interno que o cliente reclamar antes da correção passa ao prazo de cliente a partir da reclamação (vincular o ticket ao card e recalcular o SLA).

Cálculo da data (Priority P3 fica sem SLA; CATASTRÓFICO é o próprio dia da criação):

```bash
# N-ésima janela de deploy (terça ou quinta) contando a partir do dia seguinte à criação
sla_janelas() { d="$1"; n=0; while [ "$n" -lt "$2" ]; do d=$(date -d "$d +1 day" +%F); case $(date -d "$d" +%u) in 2|4) n=$((n+1));; esac; done; echo "$d"; }

CRIACAO=$(date +%F)
sla_janelas "$CRIACAO" 6               # Priority P2, card interno
sla_janelas "$CRIACAO" 4               # Priority P1, card interno
date -d "$CRIACAO +4 day" +%F          # Priority P0, card interno
```

## Onde a severidade vai

| Quem chama | Onde grava | Mapeamento |
|---|---|---|
| `flow-bug-card` (card criado por dev, QA ou qualquer pessoa no Claude Code) | Project #7: campos **Severity**, **Priority** e **SLA** do card, logo depois de criar. A justificativa vai num **comentário** do card (o body segue o render do form). Label de bug é só `work: bug` (as `bug:low/medium/high/critical` não se usam mais). | Severity: P3, P2, P1, P0, CATASTRÓFICO. SLA: data da tabela acima, pela Priority. |
| Pipe do suporte (ticket em N3) | HubSpot, campo Prioridade (`prioridade_tech`, um valor só). O n8n leva pra Severity do card quando o ticket entra em Enviado para Tech. Não mexer em Project #7 nem label. | Baixo → Baixa, Médio → Média, Alto → Alta, Crítico → Crítico. Catastrófico não existe no campo: grava Crítico e avisa. |
| Detetives (card interno de detecção proativa) | Campo Severity e SLA do card no Project #7, depois do ok do Solon pra criar o card. | P3, P2, P1, P0, CATASTRÓFICO |
| Medição de concordância | Só no log local de medição. Nunca grava no board. | igual ao GitHub |
| Pedido avulso na conversa | Só responde. Gravar em card ou ticket exige o pedido explícito. | |

IDs do Project #7 (projeto `PVT_kwDOCAubUc4BQdrV`):

| Campo | Field ID | Opções |
|---|---|---|
| Severity | `PVTSSF_lADOCAubUc4BQdrVzhhJY54` | CATASTRÓFICO `35bd739a`, P0 `2ec62f0a`, P1 `4d92058f`, P2 `3d5f60b7`, P3 `557facf9` |
| Priority | `PVTSSF_lADOCAubUc4BQdrVzg-k1Ns` | CATASTRÓFICO `838ddbc0`, P0 `79628723`, P1 `0a877460`, P2 `da944a9c`, P3 `56c0a104` |
| SLA | `PVTF_lADOCAubUc4BQdrVzg-owLg` | data (GraphQL `updateProjectV2ItemFieldValue` com `value: { date: "YYYY-MM-DD" }`) |

Severity e Priority têm os mesmos nomes de opção mas **IDs diferentes**: não reaproveite o ID de um no outro.

Sobrescrever um valor que o time já tinha posto é permitido, mas sempre mostre o antes e o depois.

## Lote grande

Mais de 10 bugs de uma vez: um subagente `general-purpose` com `model: sonnet` por lote de até 40 (Sonnet concordou 92% com Opus no teste de 08/10), no máximo 3 em paralelo, usando `prompt_lote.md` desta pasta (troque LOTE e SAIDA). Junte os resultados e confira Críticos e confiança baixa antes de entregar.

## Histórico da régua

- v0.1 a v0.3: calibração cega em 469 bugs (v0.3: 73% exato, 97% até 1 nível, os 6 Críticos reais acertados).
- v0.5 (08/10): 64% exato e 99% até 1 nível em 100 cards com Severity pós 02/09; 123 de 125 revisões do Solon concordaram.
- v0.7 (08/10): IA do WhatsApp Commerce vira Médio com Priority P1. Testada em produção de 08 a 10/10 e aprovada pelo Solon em 10/10/2026, quando a régua saiu do arquivo e virou skill.
- 19/10/2026: a skill passa a viver no `Zoppy-crm/.github` (grupo `shared`, todos os repos) e entra no fluxo da `flow-bug-card`, com SLA calculado no card.
- Pontos ainda em observação (seção 10 do playbook) seguem sendo registrados quando aparecem; só viram regra com dado real e decisão do Solon.
