# Camadas

Cada submódulo (`accounts`, `templates`, `contacts`, `messaging`) tem as mesmas camadas. "Do mesmo"
significa do mesmo submódulo. Tudo o que não está liberado aqui o lint proíbe.

| De | Pode importar |
|---|---|
| access | application e api do mesmo; domain/values do mesmo; public |
| application | domain inteiro do mesmo; api de outro submódulo; portas do platform |
| domain | só domain do mesmo; núcleo de @Zoppy-crm/exceptions |
| repository | domain/ports, model e values do mesmo; portas do platform; models Wpp* |
| infrastructure | domain/ports e values do mesmo; portas do platform |
| api | só os próprios tipos |
| public | nada interno |

A seta aponta sempre para dentro: quem está fora conhece o domain, o domain não conhece ninguém.

## public

O contrato do módulo com o resto do app.

- **Tem:** interfaces das fachadas (`MessagingFacade`), Commands com tipos primitivos (`SendTemplateCommand`), tokens de injeção (`MESSAGING_FACADE`), tipos dos eventos publicados (`MessageReceivedV1`), erros públicos.
- **Não tem:** classe com lógica, função, import de qualquer pasta interna.
- **Acordo:** mudar um tipo daqui é mudar contrato. Campo novo é opcional; campo removido exige versão nova do evento ou da fachada.

## api

O contrato entre submódulos irmãos.

- **Tem:** a interface (`ContactsApi`), os tipos de leitura que ela devolve (`ContactForSending`) e o token.
- **Não tem:** import de `domain/`. Por isso nunca devolve um agregado.
- **Acordo:** operações com nome de negócio, de leitura ou de escrita (`findForSending`, `block`, `refreshWindow`). Nunca `update`, `save`, `delete` ou `upsert` genéricos: quem chama não monta estado de outro submódulo.

## access

A borda de entrada: tudo o que chega de fora entra por aqui.

- **Tem:** a implementação da fachada (`MessagingFacadeImpl`) e do `api/` (`ContactsApiImpl`), controllers HTTP, processors de fila, consumidores de SQS, e os mappers Command → Input (`toSendTemplateInput`).
- **Faz:** converte primitivos em objetos de valor (`PhoneE164.parse`), chama a application, traduz `ZoppyError` em `ZoppyException` (HTTP) ou em retry (fila), loga entrada, saída e erro.
- **Não faz:** regra de negócio; chamar agregado diretamente (só enxerga `domain/values`); falar com repository ou infrastructure.

## application

Orquestra um caso de uso.

- **Nome:** `XApplication` (`MessagingApplication`).
- **Faz:** carrega pelos ports e pelo `api/` dos irmãos, chama a fábrica ou o método do agregado, salva, agenda fila, publica evento, loga decisões de orquestração.
- **Recebe:** um Input com objetos de valor, nunca primitivos soltos.
- **Não faz:** injetar outra application; importar repository ou infrastructure (só os ports); importar `api/` do próprio submódulo.

## domain/model

Agregados e entidades.

- **Faz:** guarda as invariantes. A regra "pode enviar?" é a fábrica `Message.createTemplate(...)`, não um serviço à parte. Transições de estado são métodos (`markSent`, `markFailed`).
- **Não faz:** I/O, log, ler config, conhecer Sequelize.
- **Referência a outro agregado:** só por id.

## domain/values

Objetos de valor e erros do domínio.

- **Objeto de valor:** imutável, validado na criação (`PhoneE164.parse` lança se inválido), igualdade por valor.
- **Erro:** subclasse de `ZoppyBaseError` com `category` e `errorType`.

## domain/ports

Interfaces que o lado de fora implementa: `MessageRepository`, `MetaGateway`, `DispatchQueue`.

- **Nome:** o conceito, sem tecnologia. A implementação leva a tecnologia no nome (`SequelizeMessageRepository`, `WhatsappV2MetaGateway`, `BullMqDispatchQueue`).
- **Assinatura:** só tipos do domain.

## repository

Persistência do submódulo dono da tabela.

- **Tem:** `SequelizeXRepository implements XRepository` e o mapper model ↔ agregado.
- **Faz:** filtra por `tenantId` de forma explícita (não herda o filtro do `RepositoryAdapter`). Grava todas as colunas que o código legado ainda lê.
- **Única camada** que importa models `Wpp*`, inclusive `include` por nome.

## infrastructure

Adaptadores para o mundo externo.

- **Tem:** `WhatsappV2MetaGateway implements MetaGateway`, `BullMqDispatchQueue implements DispatchQueue`.
- **Enxerga:** só `domain/ports` e `domain/values`, o contrato que implementa. Nunca um agregado.
- **Faz:** loga a chamada externa (destino, duração, resultado). Fila com `@InjectRingQueue`.

## Arquivos na raiz do submódulo

- `<sub>.config.ts`: `registerAs` com schema zod. Único lugar com `process.env`.
- `<sub>.logs.ts`: enum de identificadores de log `WHATSAPP_<SUB>_<FATO>`. Não pode ser importado pelo domain.
- `<sub>.module.ts`: liga tokens a implementações (`{ provide: MESSAGE_REPOSITORY, useClass: SequelizeMessageRepository }`) e exporta só tokens de `api/`.

## platform

Portas reutilizáveis por qualquer módulo: `context`, `logging`, `queue`, `events`, `inbound`.

- De fora, só `*.port.ts`. `adapters/` nunca é importado; quem faz o binding é o módulo do platform.
- O platform não importa `modules/` nem o CRM.
