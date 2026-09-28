# Catálogo de entradas

Para cada dimensão, as classes que costumam quebrar. Os exemplos são defeitos reais que passaram por specs existentes.

| Dimensão | Classes | Defeito real |
|---|---|---|
| **String** | vazia · só espaços · caixa diferente · espaço nas pontas · formato alternativo (máscara, DDI) | `fullName = '   '` passava em `!!fullName` e virava nome canônico (#9629). E-mail do vendedor com caixa diferente casava no MySQL e não no `===` (#11064) |
| **Número** | 0 · 1 e o valor do limite · negativo · `NaN`/`Infinity` · sentinela (`0`, `-1`) | `NaN` em campo NUMBER tratado como preenchido (#11527). Sentinela `vindiId = 0` gravado como `"0"` (#10523) |
| **Campo opcional** | ausente (`undefined`) · `null` · presente | `account_update` sem `waba_info` derrubava o job (#11700). Giftback sem `maxPercentValue` zerava o mínimo de compra (#11207) |
| **Referência externa** (id no provedor, wcId) | ausente · `"undefined"` · uuid vs numérico · formato legado vs novo do payload | Cupom sem `wcId` chamava o provedor com id nulo (#10701). Categoria lida por `id` em vez de `wcId` (#9770) |
| **Coleção** | vazia · 1 · N > 1 · itens com mesmo nome · mesmo dono com N registros | Contato com mais de uma conversa (#9247). Dois giftbacks no mesmo telefone (#11060) |
| **Estado prévio no banco** | vazio · já existe (2ª execução) · existe com valor divergente · soft-deleted | Atribuir features duas vezes duplicava (#9305). Pedido re-datado não propagava para a ação já existente (#10494) |
| **Volume do estado** | poucos registros · muitos registros pré-existentes que o código lê | Dedup lia todas as tasks da campanha a cada bloco (#11424) |
| **Sessão** | cada role (não só MASTER) · MANAGER com lojas · user global sem `companyId` · token com propósito restrito | Gerente via usuários de todas as lojas (#9083). Refresh aceitava token de giftcard e devolvia token pleno (#11090) |
| **Ambiente** | cada valor de `NODE_ENV` que existe (production, staging, mirror, local, test) | Em `mirror`, webhook caía no stub com URL configurada (#11406) |
| **Pontos de entrada** | a mesma regra em cada caminho que lê ou escreve o dado | Propósito do token checado no middleware e não no refresh (#11090) |
| **Serialização** | valor que passa por JSON/Redis/fila e volta | Data voltava como string do cache (#10478) |
| **Combinação de variantes** | cada tipo × cada flag relevante | Upsell produto-only com franquia de coin não creditava coin (#11565) |
| **Escopo de uma regra** | a regra (limite, bloqueio, cobrança) aplicada a uma variante onde ela não vale | Limite de retentativa de cartão bloqueava reemissão por PIX e boleto (#9174) |
| **Intervalo** | início = fim · início > fim · fim no passado sem início · um lado ausente | Janela retroativa com `minDate > maxDate` não gerava nada e ficava muda (#10766) |
| **Data do evento** | evento processado em dia diferente do que ele pertence (webhook atrasado, reprocessamento) | Delta datado com `today()` e não com a data de ativação do alerta (#10096) |
| **Valor derivado** | campo copiado de outra entidade: a fonte certa × uma fonte parecida | Gateway do item copiado do catálogo em vez da fatura (#7829) |
| **Mapeamento de tipo/enum** | cada valor que existe no enum de origem, inclusive os pouco usados | `DataType.NUMBER` sem entrada no mapa caía no fallback `text` (#9775) |
| **Update parcial** | campo que o payload não traz: é preservado ou vira default? | Editar só o nome zerava `sendRetroactive` (#9740) |
| **Status intermediário** | cada status que a entidade pode ter, não só o inicial e o final | Template em `PENDING_DELETION` fazia o delete falhar para sempre (#11164) |
| **Leitura por outro caminho** | o mesmo campo devolvido por cada rota ou método que lê a entidade | `landingScreen` vinha no login e sumia no `/companies/mine` (#10686) |
