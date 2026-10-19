# Playbook de Severidade de Bugs Zoppy

*Versão 0.7 · em produção desde 10/10/2026 (testada de 08 a 10/10) · Dono: Supervisão de Suporte Técnico*

*Fonte oficial: skill `severidade-bugs` no repo `Zoppy-crm/.github` (`skills/shared/severidade-bugs/playbook.md`), sincronizada para `.claude/skills/severidade-bugs/` de todos os repos. Mudança de regra só por PR nesse repo. O Google Doc "Playbook de Severidade de Bugs Zoppy" é espelho dela.*

Este documento é a fonte única para classificar a **severidade** de um bug na Zoppy. Ele foi escrito para ser lido por pessoas e por qualquer agente de IA que classifique ou reclassifique severidade. A IA segue as regras na ordem em que aparecem e devolve a resposta no formato da seção 9.

### Como esta versão foi calibrada

O playbook foi aplicado às cegas (sem ver a severidade do board) em 469 bugs reais de master e comparado com a Severity que o time deu desde 02/09/2026, quando Severity e Priority viraram campos separados.

| Versão | Críticos dados (469 bugs) | Nível exato igual ao time | Até 1 nível de diferença |
|--------|---------------------------|---------------------------|--------------------------|
| v0.1   | 92                        | 33%                       | não medido               |
| v0.2   | 6                         | 63%                       | 98%                      |
| v0.3   | 6                         | 73%                       | 97%                      |

Na v0.3 os 6 Críticos reais do time foram identificados e nenhum outro bug recebeu Crítico. As versões 0.4 e 0.5 acrescentam decisões do Supervisor de Suporte (abaixo); a v0.5 foi medida em 08/10/2026 (parágrafo seguinte). A regra de integração da v0.5 é uma decisão de como o time **deve** classificar daqui pra frente: ela vai divergir de alguns cards antigos que o time deu Médio.

**Medição da v0.5 (08/10/2026).** Aplicada às cegas em 526 cards de cliente e CSM (abril a outubro). Só 100 têm Severity do time dada depois da separação entre Severity e Priority (02/09/2026) e servem de comparação: 64% de nível exato e 99% com até 1 nível de diferença. 31 desses 100 são exemplos citados neste playbook; sem eles, o acerto exato é 52% (69 cards), com 99% até 1 nível. A divergência é simétrica: 17 cards abaixo do time e 19 acima. Nenhum card recebeu Crítico. Os 125 cards selecionados para revisão (a maioria de confiança baixa) foram revisados pelo Supervisor de Suporte: 123 concordam com o nível do playbook e 2 são Não bug, igual ao playbook.

**Regra de calibração:** cards citados como exemplo neste playbook ficam fora da amostra de medição, porque inflam o acerto.

**Decisões de 06/10/2026:**

- Reincidência não muda a severidade (vai para Priority).
- Automação que só atrasa não é Alto, só a que deixa de rodar.
- Acesso indevido dentro da mesma empresa é sempre Alto.
- Card retroativo de um incidente recebe a mesma severidade do incidente.
- Card de integração com entrada de dados é Alto, mesmo numa empresa só e mesmo pontual.
- Campo personalizado de integração é Alto só se alimenta fluxo, segmento ou mensagem.
- Cobrança que a Zoppy deixa de emitir é Médio pontual e Alto sistêmica.

**Decisão de 08/10/2026 (v0.7):** card de **IA do WhatsApp Commerce** tem severidade **Médio (P2)** e Priority **P1**. A IA do WhatsApp Commerce deixa de ser função "sempre Alto". Os gatilhos de Crítico (seção 5.4) e Catastrófico (seção 5.5) continuam valendo antes: se a falha tiver os três critérios do Crítico ou for queda para a base inteira, sobe pelas regras de sempre.

## 1. Severidade não é prioridade

| Campo        | O que mede                                                                 | Quem influencia                                                              |
|--------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------|
| **Severity** | O tamanho do estrago do bug: o que quebra, para quantos, e se tem contorno | Só o bug em si                                                               |
| **Priority** | A ordem em que a engenharia ataca                                          | Severidade + contexto (HighTouch, contrato, momento comercial, reincidência) |

**Regra:** cliente HighTouch e reincidência **não mudam a severidade**. Eles entram só no campo Priority. A IA do WhatsApp Commerce segue o mesmo princípio: severidade Médio (P2) e Priority P1 (decisão de 08/10/2026). No GitHub, os dois campos têm as mesmas cinco opções: CATASTRÓFICO, P0, P1, P2, P3.

A severidade alimenta o Score de Severidade (CATASTRÓFICO×16 + P0×8 + P1×4 + P2×2 + P3×1), que mede qualidade do produto. Por isso ela não pode ser inflada por contexto comercial.

## 2. A régua do time (dados reais desde 02/09/2026)

| Nível        | Cards | %   | Cliente/CSM |
|--------------|-------|-----|-------------|
| Catastrófico | 0     | 0%  | 0           |
| Crítico (P0) | 6     | 3%  | 0           |
| Alto (P1)    | 78    | 39% | 31          |
| Médio (P2)   | 92    | 46% | 68          |
| Baixo (P3)   | 24    | 12% | 10          |

Crítico é raro e, nesse período, só veio de achado interno. Se a IA estiver dando Crítico em mais de 1 a cada 20 bugs, está errando.

## 3. Quando classificar e quem decide
- A IA classifica a severidade quando o ticket está em **N3**, depois da investigação, e quando um card de bug é criado no Claude Code (skill `flow-bug-card`) ou um card interno é proposto (dev, QA, Detetive, alerta, revisão).
- Desde 10/10/2026 a IA **aplica direto** em Baixo, Médio, Alto e Crítico (decisão do Supervisor de Suporte depois do teste em produção). Crítico é aplicado e destacado para revisão. **Catastrófico nunca é aplicado sozinho:** a IA para e avisa o Supervisor, que decide a War Room.
- O time pode corrigir depois; quando a IA troca um valor que o time já tinha posto, mostra o antes e o depois.
- Depois que o card existe, reclassificar exige alinhamento com Produto. A IA pode sugerir reclassificação quando surgir fato novo.

## 4. Passo zero: é bug?

Bug é quando o sistema não faz o que a regra atual de produto manda. Se não for, **não pontua**.

| Categoria                 | O que é                                                                       | Exemplo                                           |
|---------------------------|-------------------------------------------------------------------------------|---------------------------------------------------|
| Mal uso                   | Configuração incorreta feita pelo cliente                                     | Fluxo com gatilho errado montado pelo lojista     |
| Dúvida                    | Comportamento esperado da plataforma                                          | Cliente Campeão no RFM com compra antiga          |
| Configuração inicial      | Pendência de implantação ou credencial                                        | Número não verificado na Meta, DNS não apontado   |
| Melhoria                  | Sistema age como a regra manda, mas a regra precisa mudar                     | Deduplicar pedido entre ERP e e-commerce          |
| Solicitação de dados      | Pedido de alteração, correção ou exclusão de dado                             | Excluir lojas criadas por planilha errada         |
| Instabilidade de terceiro | Meta, ERP, plataforma ou gateway fora do ar, ou parceiro que não envia o dado | Convertr não chama o endpoint de carrinho         |
| Dado errado na origem     | O provedor manda o dado errado e a Zoppy grava o que recebeu                  | VNDA enviando wcId de categoria duplicado (#9770) |
| Duplicado                 | Card do mesmo ticket ou incidente que outro card já pontua                    | Registrar como "Duplicado do #número"            |
| Teste interno             | Card criado pelo time para teste, sem cliente afetado                         | Card com título de teste e sem relato             |

Se o terceiro falha **e a Zoppy trata mal a falha** (perde o dado, não registra, mostra sucesso falso), a parte da Zoppy **é bug**. Card duplicado do mesmo ticket: só um pontua.

## 5. Os cinco níveis

| Nível        | GitHub Severity | Pontos | Prazo da engenharia                                                    |
|--------------|-----------------|--------|------------------------------------------------------------------------|
| Baixo        | P3              | 1      | Sem prazo travado, fila do produto                                     |
| Médio        | P2              | 2      | 3 janelas de deploy (ter/qui)                                          |
| Alto         | P1              | 4      | 2 janelas de deploy (ter/qui)                                          |
| Crítico      | P0              | 8      | 2 dias corridos, correção emergencial fora da janela quando necessário |
| Catastrófico | CATASTRÓFICO    | 16     | Resposta imediata, contenção em horas, War Room                        |

**Prazo do card interno** (achado antes do cliente: monitoramento, Detetive, alerta, IA, revisão; sem `client:report`), decisão do Solon em 10/10/2026: **o dobro do card de cliente**.

| Nível        | Card de cliente                | Card interno                                   |
|--------------|--------------------------------|------------------------------------------------|
| Baixo        | Sem prazo travado              | Sem prazo travado, revisão em 30 dias corridos |
| Médio        | 3 janelas de deploy (ter/qui)  | 6 janelas de deploy (cerca de 3 semanas)       |
| Alto         | 2 janelas de deploy            | 4 janelas de deploy (cerca de 2 semanas)       |
| Crítico      | 2 dias corridos                | 4 dias corridos                                |
| Catastrófico | Imediato, War Room             | Imediato, War Room (não muda)                  |

Janelas contadas a partir do dia seguinte à criação do card. **Se o cliente reclamar do mesmo problema antes da correção**, o card interno passa a seguir o prazo de cliente a partir da data da reclamação (vincular o ticket ao card).

### 5.1 Baixo (P3)

Visual, texto, ergonomia, ferramenta interna com mensagem de erro ruim, diferença de centavo, recurso acessório com contorno imediato. Nada muda no resultado da operação.

Também é Baixo: **job interno travado ou lento sem efeito visível para o cliente** (#11285, #11327) e **caso raro de checkout com contorno** (#11995, #11997, #12237).

Exemplos reais: ícone pequeno na Área de Clientes (#12063); campo de e-mail do login com comportamento de senha (#11955); total com desconto um centavo diferente da fatura (#11976); erros mudos nas tools do MCP (#11926, #11928); mapeamento de campos visível só para master (#11655).

### 5.2 Médio (P2): o nível mais comum

Função quebrada **para uma empresa** (ou poucos consumidores dela) com contorno, **ou dado e conteúdo errados de forma pontual**, mesmo quando chegam ao consumidor final. "Pontual" quer dizer: causado por uma ação específica (subida de planilha, import manual, edição de template), por conteúdo de mensagem (variável vazia ou errada) ou por uma condição rara. Se o dado errado vem de **integração com provedor**, é Alto, mesmo pontual.
- Variável vazia em mensagem enviada ao consumidor, numa empresa (#12010, #11128)
- Pedido importado por planilha vinculado ao cliente errado (#11658) ou não vinculado (#11110)
- Exclusão de planilha apagando 374 clientes de uma empresa (#12281)
- Mensagem de entregue para pedido não entregue, numa empresa (#11566)
- Giftback indevido gerado numa empresa (#11525)
- Campanha de uma empresa travada em ON_HOLD (#11538)
- Cobrança que a Zoppy deixa de emitir, pontual (#12294, #12307, #12308). Quando é sistêmica (todas as empresas de um gateway ou tipo de plano), é Alto
- Carrinho abandonado disparado para quem já comprou, numa loja (#12111)
- Automação que só atrasa ou falha em casos isolados; integração que só atrasa sem perder dado
- Campo personalizado de integração que não chega, quando não é usado em nada ativo
- **IA do WhatsApp Commerce** respondendo errado ou falhando: preço errado, catálogo indisponível, configuração que não salva, contatos sem resposta da IA (#11073, #12113, #12066, #11598, #12567, #12577, #12579). Severidade Médio (P2), Priority P1. A IA registra Priority P1 na sugestão

### 5.3 Alto (P1)

1.  **Uma das três funções que o time sempre trata como Alto, mesmo numa empresa só:**

    - **Integração com entrada de dados**: dado vindo do provedor (ERP, e-commerce, Partners API, webhook de parceiro) que não entra, entra errado, entra duplicado ou é descartado. Vale para pedido, cliente, cupom, produto, status e devolução, **mesmo numa empresa só e mesmo em caso pontual** (#12310, #12070, #12298, #12359, #11076, #12412, #12006). Exceções:

      - **Campo personalizado** mapeado da integração: Alto **só se o campo alimenta algo ativo** da empresa (gatilho ou condição de fluxo, regra de segmento, variável de template ou de mensagem). Se não é usado em nada ativo, é Médio. A IA verifica o uso do campo na empresa; se não conseguir, classifica Médio e registra a pergunta "o campo X é usado em fluxo, segmento ou mensagem?".
      - **Dado errado na origem** (o provedor manda o dado errado e a Zoppy grava o que recebeu) não é bug (categoria Dado errado na origem, seção 4).
      - Integração que só **atrasa**, sem perder nem corromper dado, segue a matriz.
    - **Automação que deixa de rodar**: fluxo que não dispara, etapa de fluxo que falha, gatilho que perde a configuração, tarefa que não é criada (#11486, #11378, #11360). Automação que só atrasa não entra aqui.
    - **Cobrança, upsell ou fatura da Zoppy** cobrando errado ou sem entregar o que foi contratado (#11911, #11984, #11986, #11991).

2.  **Função central parada sem contorno** para a empresa, fora das três acima (Painel do Vendedor não deixa realizar tarefa, integração do WhatsApp não conclui).

3.  **Erro sistêmico de lógica**: acontece para toda empresa que usa a função, mesmo sem dinheiro envolvido (#11647, #11577).

4.  **Acesso indevido dentro da mesma empresa**, sempre Alto, seja para ver ou para agir (#9083, #9655, #10254). Se o acesso for a **outra empresa**, é candidato a Crítico ou Catastrófico.

5.  **Dinheiro ou dado errado com alcance além de uma empresa** (#11207, #11565, #12407), cobrança não emitida de forma sistêmica, ou **exposição de segredo ou dado sensível sem acesso de outra empresa** (#11510, #11623).

### 5.4 Crítico (P0): raro

Só entra com **os três ao mesmo tempo**:

1.  **Fluxo inteiro** afetado, não um caso: todas as empresas de um gateway, de um provedor ou de uma funcionalidade.

2.  **Sem contorno** para o cliente.

3.  **Dinheiro ou segurança** em jogo: o cliente não consegue pagar, dinheiro é cobrado sem registro, dinheiro vaza sem ninguém ver, ou uma empresa consegue acessar outra.

| Card    | O que era                                                                 | Por que é Crítico                                                   |
|---------|---------------------------------------------------------------------------|---------------------------------------------------------------------|
| #11090 | Credencial de parceiro emite token MASTER de qualquer empresa             | Uma empresa (ou parceiro) consegue controlar outra                  |
| #11974 | Pix da Vindi nunca gera código no checkout                                | Ninguém consegue pagar por esse caminho                             |
| #11973 | QR do Pix da Malga recusado pelo banco                                    | Ninguém consegue pagar por esse caminho                             |
| #11980 | Cliente não consegue trocar Pix por cartão e entra em loop sem pagar      | Pagamento bloqueado, sem contorno                                   |
| #11983 | Upsell cobra o cartão e não cria fatura                                   | Dinheiro cobrado sem registro                                       |
| #11919 | Cupom cancelado na Zoppy continua válido na loja Magazord (77 falhas/dia) | Dinheiro do lojista vazando em todo o provedor, sem erro registrado |

O que **não** é Crítico, mesmo parecendo grave: dado errado ou apagado numa empresa; conteúdo errado entregue a consumidores de uma empresa; variante do fluxo de pagamento com contorno (Pix com CNPJ, #11972; cartão recusado demorando 18 min, #11975; webhook de pagamento não confirmado, #11978); segredo exposto em log interno; acesso indevido dentro da mesma empresa. Todos esses são Alto ou Médio.

### 5.5 Catastrófico (War Room)

1.  Plataforma ou módulo central fora do ar para a base inteira (login geral, #10294; envio de WhatsApp de todos; processamento de pedidos parado).

2.  Vazamento ou acesso entre empresas **explorado**, ou dado de uma empresa aparecendo para outra.

3.  Perda ou corrupção de dados em massa **com efeito real** (cobrança, disparo ou pedido errado em centenas de empresas).

Não abre War Room: dado errado em massa sem efeito operacional ainda. Card retroativo de um incidente já resolvido recebe a severidade do incidente, inclusive Catastrófico, mas não abre War Room depois do fato.

## 6. Algoritmo de decisão

**Etapa 1. É bug?** (seção 4). Se não, devolver "não pontua" e parar.

**Etapa 2. Gatilho Catastrófico?** (seção 5.5). Se sim, Catastrófico e parar.

**Etapa 3. Teste do Crítico.** Os três critérios da seção 5.4 estão presentes **e confirmados no card**? Se sim, Crítico. Se falta qualquer um, segue.

**Etapa 4. Funções sempre Alto.** É integração com entrada de dados, automação que deixa de rodar, cobrança da Zoppy ou acesso indevido dentro da empresa? Se sim, Alto (respeitando as exceções da seção 5.3). **IA do WhatsApp Commerce não entra aqui:** é Médio (P2) com Priority P1, depois de passar pelas Etapas 2 e 3.

**Etapa 5. Gravidade × alcance** para o resto.

| Código | Gravidade                                                                | Exemplos                                                                                          |
|--------|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| G1     | Visual ou ergonomia                                                      | Layout, texto, mensagem de erro ruim, centavo                                                     |
| G2     | Funcional com contorno, ou exibição errada                               | Relatório divergente, filtro, exportação, tela de consulta                                        |
| G3     | Função central parada sem contorno, ou dado, dinheiro ou conteúdo errado | Fluxo de envio parado, variável vazia enviada, cupom errado, pedido de planilha no cliente errado |

| Código | Alcance   | Como reconhecer                                                                                            |
|--------|-----------|------------------------------------------------------------------------------------------------------------|
| A1     | Pontual   | Uma empresa, ou um caso dentro dela. Outra empresa no título sem evidência no corpo continua sendo pontual |
| A2     | Sistêmico | Acontece no uso normal para toda empresa que usa a função, provedor ou gateway, confirmado no card         |

|        | A1 Pontual                                                    | A2 Sistêmico                                                      |
|--------|---------------------------------------------------------------|-------------------------------------------------------------------|
| **G1** | Baixo                                                         | Baixo                                                             |
| **G2** | Médio                                                         | Alto se afeta decisão do cliente (segmento, receita), senão Médio |
| **G3** | Médio, ou Alto se a função central está parada para a empresa | Alto                                                              |

**Reincidência não muda a severidade**: vai para Priority.

**Etapa 6. Conferir com a régua.** Comparar com os exemplos reais da seção 5. Na dúvida entre dois níveis, escolher o **menor** e registrar a dúvida.

## 7. Definições
- **Consumidor final:** o cliente da loja. Diferente do lojista, que é o cliente da Zoppy.
- **Parada vs degradada:** parada é quando a empresa não consegue usar a função de jeito nenhum. Degradada é quando funciona com falhas, atraso ou para parte dos casos.
- **Teste vs envio real:** erro só no teste de envio ou preview é G2.
- **Sistêmico vs potencial:** sistêmico é quando o defeito acontece no uso normal para toda empresa que usa a função. Potencial é quando depende de condição incomum. Potencial conta como Pontual.
- **Fluxo de receita da Zoppy:** método de pagamento inteiro quebrado no gateway é Crítico ("pagar por outro método" não conta como contorno); cobrança errada ou contratado não entregue é Alto; subcaso do método, demora ou pagamento bloqueado numa empresa só é Alto; cobrança não emitida é Médio pontual e Alto sistêmica; caso raro com contorno ou diferença visual é Baixo.
- **Card retroativo de incidente:** recebe a mesma severidade do incidente. Se já existe um card do mesmo incidente com severidade definida, repetir essa severidade.
- **Terceiro que falha e a Zoppy esconde:** a parte da Zoppy herda a gravidade do que ficou escondido.
- **Contorno que só o time interno consegue fazer** (script, Swagger, ajuste no banco): conta como sem contorno para o cliente.

## 8. Erros que a IA não pode cometer

1.  Usar HighTouch, tamanho do cliente ou tom do relato para mudar a severidade. Isso é Priority.

2.  Dar Crítico para dado ou conteúdo errado numa empresa só.

3.  Dar Crítico sem os três critérios confirmados no card.

4.  Tratar "outra empresa no título" como alcance sistêmico sem evidência no corpo.

5.  Tratar alcance potencial como sistêmico.

6.  Subir a severidade porque o bug é reincidente.

7.  Pontuar instabilidade de terceiro quando a Zoppy tratou a falha corretamente.

8.  Dar Médio para card de integração com entrada de dados (fora as exceções da seção 5.3).

9.  Misturar casos: a justificativa cita apenas o ticket analisado.

10. Dar Alto para falha da IA do WhatsApp Commerce só por ser a IA. A regra é Médio (P2) com Priority P1; só sobe se os gatilhos de Crítico ou Catastrófico forem confirmados.

## 9. Entradas e saída do agente

Entradas: subject, content, relato_do_cliente, interpretacao_do_csm, `ops__comportamento_atual`, `ops__comportamento_esperado`, categoria_do_ticket, funcionalidade, doc de evidência e doc de investigação. Para campo personalizado de integração, a IA também verifica se o campo é usado em fluxo, segmento ou template ativo da empresa. `prioridade__categoria_do_ongoing` (HighTouch) e reincidencia **não entram** na severidade; a IA pode repassá-los para a sugestão de Priority.

```json
{
  "ticket_id": "string",
  "eh_bug": true,
  "categoria_se_nao_bug": "mal_uso | duvida | configuracao_inicial | melhoria | solicitacao_de_dados | instabilidade_terceiro | dado_errado_origem | duplicado | teste_interno | null",
  "nivel": "Baixo | Médio | Alto | Crítico | Catastrófico",
  "github_severity": "P3 | P2 | P1 | P0 | CATASTRÓFICO",
  "pontos": 4,
  "gravidade": "G1 | G2 | G3",
  "alcance": "A1 | A2",
  "funcao_parada": true,
  "funcao_sempre_alto": "integracao | automacao | cobranca_zoppy | acesso_indevido | null",
  "priority_sugerida": "P1 | null",
  "teste_critico": {"fluxo_inteiro": false, "sem_contorno": true, "dinheiro_ou_seguranca": false},
  "justificativa": "2 a 4 frases, só fatos deste ticket",
  "exemplo_real_mais_parecido": "#numero",
  "confianca": "alta | média | baixa",
  "perguntas_pendentes": [],
  "requer_confirmacao_humana": false,
  "acionar_war_room": false
}
```

requer_confirmacao_humana = true quando o nível for Crítico ou Catastrófico, a confiança for baixa ou houver perguntas pendentes. `priority_sugerida` = "P1" quando a funcionalidade for IA do WhatsApp Commerce; nos demais casos, null (a Priority é definida pelo time).

## 10. Pendências de definição

Decisão de 08/10/2026: a v0.6 seguia as regras da v0.5 sem alterar nenhum nível; a v0.7 muda só a IA do WhatsApp Commerce (Médio com Priority P1). O teste em produção terminou em 10/10/2026 com a régua aprovada. Os pontos abaixo continuam em observação e só viram mudança de regra com dados reais.
- **IA do WhatsApp Commerce em Médio (P2) com Priority P1** (decisão de 08/10/2026; antes era Alto: #11073, #12113, #12066, #11598, #12567, #12577, #12579): observar se algum caso pede nível maior, por exemplo IA parada para todas as empresas ou preço errado chegando ao consumidor em volume.
- **Contato bloqueado, em blacklist ou com opt-out recebendo disparo** (#8142, #10148, #9026): segue a matriz, Médio quando pontual. Observar casos em mais de uma empresa.
- **Recurso fora do plano acessível** (#11255, #12008): segue a matriz, Médio.
- **Valor padrão do provedor gravado como dado válido** (#12309): segue como Alto, em integração com entrada de dados. Observar se a regra de dado errado na origem gera dúvida.
- **Código de acesso ou 2FA que não chega** (#9110 e #10153 Médio; #11654 e #9732 Não bug por terceiro): sem regra nova. Observar se o critério (card cita o provedor ou não) gera inconsistência.
- **Templates do WhatsApp reprovados após reconexão** (#10898 Médio, #11549 Alto): níveis mantidos. Observar se o mesmo comportamento volta com níveis diferentes.
- **Automação: deixa de rodar contra falha isolada** (#11360 ficou Médio na medição, embora a seção 5.3 o cite como exemplo de Alto; #6894 Médio; #11903 Alto): sem regra nova. Observar a fronteira entre os dois.
- **Label do card contradiz o conteúdo ou duplicado provável** (#11556 com fakeBug segue Alto; #6059 Alto e #6053 Médio): sem regra nova.
