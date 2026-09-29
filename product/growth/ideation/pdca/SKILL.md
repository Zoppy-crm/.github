---
name: zoppy-growth-pdca
description: >
  Skill de Analise de Causa Raiz + Plano de Acao no formato PDCA da Marina. Recebe um problema especifico (geralmente desvio de KR/metrica) e estrutura em arvore Problema -> Por que -> Por que -> Acoes datadas, com Tipo da acao (Impacto/Analise), Responsavel e Prazo.

  Acionar quando houver um desvio de metrica ou KR especifico (ex: MRR abaixo da meta, taxa caiu) que precisa virar plano de acao com causa raiz mapeada e dono/prazo por acao. Substitui a matriz Confianca x Contribuicao usada antes para esse tipo de caso -- mais rapido, vai direto de causa pra acao.
---

# Analise PDCA (formato Marina) — Zoppy Growth

Voce estrutura um problema especifico em arvore de causa raiz e converte direto em plano de acao datado. Diferente da `zoppy-growth-hypothesis` (ICE), aqui nao se compara hipoteses concorrentes por score — vai direto do "por que" pra acao, priorizando por dependencia e nao por pontuacao.

**Quando usar este formato em vez do ICE:** quando ja existe um problema especifico e delimitado (um desvio de KR, uma meta nao batida) e o objetivo e sair da sessao com acoes datadas. Use `zoppy-growth-hypothesis` quando ha varias ideias concorrentes disputando prioridade e recursos limitados entre elas.

---

## Template da tabela

| # | Problema especifico | Por que? (nivel 1) | Por que? (nivel 2) | # | Acao | Tipo da acao | Responsavel | Prazo |
|---|---|---|---|---|---|---|---|---|
| 1 | [problema com o dado de desvio, ex: "Desvio de MRR de X para clientes em [mes] (R$Y)"] | [causa direta] | [aprofunda so se a causa de nivel 1 nao for acionavel direto] | 1.1 | [acao concreta] | Impacto / Analise | [nome] | [data ou "a definir"] |

**Regras de preenchimento:**

- **Problema especifico** sempre carrega o dado que evidencia o desvio (valor, %, periodo). Sem dado, nao e problema especifico — e percepcao.
- **Por que nivel 1** pode ramificar em varias causas paralelas para o mesmo problema. Nao force uma causa unica.
- **Por que nivel 2** so existe quando o nivel 1 ainda nao e acionavel diretamente (ex: "baixa geracao de demanda" precisa de mais uma camada; "pouca clareza de ICP" ja vai direto pra acao).
- **Tipo da acao:**
  - **Impacto** = acao que ataca o problema diretamente, pode comecar ja.
  - **Analise** = precisa investigar/validar antes de virar impacto (entrevista, definicao de ICP, definicao de visao de produto). Analise nao e desculpa pra adiar — tem responsavel e prazo como qualquer acao.
- **Responsavel e obrigatorio antes de datar.** Uma acao sem dono nao recebe prazo — fica marcada como gap aberto, nunca como "sem prazo" silencioso.
- **Prazo nunca e chute.** Se o dono real da decisao de prazo nao esta na sessao, nao inventar data. Marcar `a definir com [quem] ate [data da proxima checagem]` — isso evita tanto a data fantasiosa quanto o vazio sem dono do proximo passo.

**Nao duplicar "por que" quando a solucao e a mesma.** Se varias linhas de "por que" levam todas pra mesma acao de fundo (ex: "criar processo X"), colapsar numa linha so, com uma acao que referencia o processo — nao listar uma linha por sintoma quando a causa e o remedio sao identicos. Regra pratica: se ao escrever a tabela voce perceber 2+ acoes com o mesmo verbo-alvo (ex: "implementar processo", "seguir processo", "rodar processo"), sao a mesma acao, nao acoes diferentes.

**Processo detalhado vem depois do PDCA, nao antes.** Quando uma acao do PDCA e "implementar processo X" e esse processo tem varias etapas, a tabela do processo (etapas/dono/o que exige) e a **elaboracao** dessa acao — entra logo apos a tabela do PDCA e o Status da Fase, nunca como preambulo antes do problema. O PDCA e o que abre o documento (problema → causa → acao), o processo detalhado e o "como" de uma acao especifica.

**Nao bundlar problemas distintos numa frase so.** Se um "Problema" tem 2+ causas com **acoes que nao se sobrepoem** (cada uma resolve uma coisa que a outra nao resolve), sao problemas separados — usar "Problema 1", "Problema 2"... como no exemplo abaixo, cada um com seu proprio por-que e acao. So escrever um "Problema" so quando as causas realmente convergem pra mesma acao (aí sim colapsa, ver regra anterior). Teste rapido: se ao remover uma das acoes o problema continua sem solucao por outro angulo, e problema separado, nao a mesma coisa reformulada.

---

## Sequenciamento (priorizar antes de datar)

Nao distribuir prazos na ordem em que as acoes aparecem na tabela. Sequenciar por dependencia real:

1. **Acoes com dependencia textual explicita** (a celula da acao ja diz o que ela desbloqueia, ex: "possibilita venda a partir de set") — prioridade maxima, datar para *antes* do inicio do periodo que dependem delas.
2. **Analise que informa Impacto** — rodar antes ou em paralelo com as acoes de impacto que dependem dela. Nao faz sentido rodar um teste de demand-gen antes de saber o ICP, por exemplo.
3. **Impacto sem dependencia** — pode comecar a qualquer momento, usar pra preencher o inicio do periodo.
4. **Impacto dependente de outra acao de impacto** (ex: testar self-service so funciona se a tela de configuracao ja existir) — datar depois da acao da qual depende.
5. **Acoes de maior lead time** (tipicamente billing, integracao, dev pesado) — comecar cedo mesmo que o responsavel ainda nao esteja 100% confirmado; sinalizar a falta de dono como risco, nao como motivo pra adiar o inicio.

---

## Exemplo real (WPP Commerce, desvio de MRR agosto/2026)

```markdown
## PDCA — Desvio de MRR WPP Commerce (R$3,5 mil, agosto/2026)

### Problema 1 — Desvio de MRR de WPP Commerce para clientes em agosto (R$3,5 mil)

| Por que? | Por que? | # | Acao | Tipo | Resp. | Prazo |
|---|---|---|---|---|---|---|
| Baixa geracao de demanda | Dependencia humana pra venda (time farmer) | 1.1 | Testar fluxo de contratacao self service | Impacto | Thiago | 18/09 |
| | | 1.2 | Testar revisao da jornada de liberacao da tela de config | Impacto | Thiago | 11/09 |
| | | 1.3 | Criar gatilhos de comunicacao in-product | Impacto | Thiago | 01/09 |
| | Cliente nao sabe da solucao | 1.4 | Criar regua de comunicacao wpp/email/pop-ups | Impacto | Thiago | 04/09 |
| Gargalo na ativacao da IA | Dependencia humana para ativacao | 1.5 | Criar tela de configuracao do WPP Commerce | Impacto | LG | Concluido (17/08) |
| Pouca clareza de ICP | | 1.6 | Entrevistar 19 clientes (F4P) | Analise | Marina | a definir com Marina ate 22/08 |
| | | 1.7 | Identificar ICP do WPP Commerce | Analise | Thiago | 28/08 |
| Nao cobramos add-on de conversas excedentes | Billing nao esta preparada | 1.8 | Estruturar billing pra cobrar add-ons | Impacto | — | a definir com MT ate 22/08 |

### Problema 2 — Nao venda de WPP Commerce para nao-clientes

| Por que? | # | Acao | Tipo | Resp. | Prazo |
|---|---|---|---|---|---|
| Atualmente nao e possivel vender separado | 2.1 | Criar plano personalizado pra WPP Commerce (possibilita venda a partir de set) | Impacto | MT | 01/09 |
| | 2.2 | Garantir que o plano acessa so chat/config IA/integracoes (possibilita venda a partir de set) | Impacto | MT | 01/09 |
| | 2.3 | Definir visao de medio/longo prazo do produto pra priorizar backlog | Analise | Marina | sem prazo — nao bloqueia setembro |
```

**Observacoes de leitura desse exemplo:**
- 2.1/2.2 foram datadas no limite exato do que a propria celula exige ("a partir de set") — dependencia textual = prioridade maxima.
- 1.3 e 1.4 (nao dependem da tela 1.5) vieram antes de 1.2 e 1.1 (que dependem dela) — sequenciamento por dependencia, nao por ordem da tabela.
- 1.7 (ICP) ficou antes de setembro comecar porque informa as acoes de demanda — analise que alimenta impacto vem primeiro.
- 1.8 sem responsavel virou gap sinalizado com data de decisao, nao prazo de entrega inventado.

---

## Onde entra na esteira

Usar como ponte entre Research/Hipoteses e Test Cards, quando o input ja e um problema especifico com dado de desvio (nao uma ideia solta). Depois do PDCA fechado, as acoes tipo "Impacto" com escopo de experimento seguem para `zoppy-growth-testcard`; acoes tipo "Analise" seguem como task de pesquisa antes de virar test card.

**Producao do bloco de Status da Fase ao final. Pedido de confirmacao obrigatorio.**

```markdown
## Status da Fase — PDCA

- **Pode avancar?** Sim / Nao / Condicional
- **N problemas mapeados:** [N]
- **N acoes com responsavel + prazo:** [N] de [total]
- **Gaps abertos (sem responsavel ou prazo indefinido):** [lista]
- **Recomendacao:** Avancar acoes de Impacto / Fechar gaps antes de avancar
- **Motivo:** [1-2 linhas]

---
Proxima fase: Test Cards (zoppy-growth-testcard) para acoes de Impacto com escopo de experimento
Growth, confirma o plano e os gaps sinalizados?
```

## Regras de comportamento

**Nunca datar acao sem responsavel.** Vira gap sinalizado, nunca prazo silencioso.

**Nunca inventar prazo que depende de decisao de terceiro.** Marcar "a definir com [quem] ate [data de checagem]".

**Priorizar por dependencia, nunca por ordem de linha da tabela.** Acao com dependencia textual explicita datada primeiro; analise que informa impacto vem antes do impacto que depende dela.

**Sinalizar acao concluida fora do prazo original como concluida, nao como atraso ativo.** Verificar sempre antes de tratar uma data passada como risco.
