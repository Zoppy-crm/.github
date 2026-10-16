# Coexistência com o legado

## A regra de base

Migrar é passar a ser o **único que grava**. Ler continua permitido ao legado até a vez dele.

- Gravar fica com um só: é na gravação que vivem as regras; dois caminhos gravando divergem.
- Ler pode continuar: mesma tabela, mesmo significado, schema só aditivo. Quem só lê fica na lista de exceções.
- Reverter é reverter o merge: o legado entende tudo o que o código novo gravou.

## As quatro situações

| Situação | Exemplo | Regra |
|---|---|---|
| 1. Legado precisa do que já migrou | Depois do F1, o envio legado lê se a conta está ativa | Só lê: continua direto, na lista de exceções. Grava: chama o `api/` ou `public/` no mesmo PR da milestone |
| 2. Código novo precisa do que não migrou | O resync da conta (F1) dispara o sync de template (F2) | O módulo não chama o legado. Quem orquestra continua sendo o chamador legado (processor, controller): chama o módulo e depois o legado, como hoje. A milestone do outro lado resolve essa chamada |
| 3. Legado mexe numa linha que o módulo criou | Depois do F4a, a mensagem nasce no módulo; até o F4b, o webhook legado da Meta acha a linha pelo `wamId` e atualiza o status | Não há evento: o legado reage à Meta, não ao módulo. O mapper grava a linha igual à do legado, com todas as colunas que ele lê. Um cenário de caracterização do lado legado usa uma linha criada pelo módulo |
| 4. Código velho e novo rodando juntos | Na drenagem do F4a.1, o processor antigo termina a fila antiga enquanto o novo já consome a nova, para a mesma empresa | Os dois usam a mesma chave do limitador no Redis (`ratelimit:whatsapp_message_sender_rate_limit:COMPANY:{companyId}`); senão cada um libera 30/s e a empresa envia 60/s |

## Colunas com donos diferentes

Uma linha pode ter dois donos por coluna durante a transição. Em `WppContacts`, o F3 assume as
colunas de canal (telefone, bsuid, nomes, `isBlocked`, `sessionExpiration`) e o atendimento continua
gravando as dele (`wppManagerId`, `status`, `hasUnread`, `lastWppMessage*`) até o F5. O repositório
do submódulo grava só as colunas que são dele.

## O chamador legado orquestra

Quando um fluxo de hoje passa por duas capacidades e só uma migrou, o módulo faz a parte dele e
devolve. Quem continua a sequência é o chamador legado, como já fazia:

```ts
await this.accounts.resync(tenantId);
await this.legacyTemplates.syncWhatsappMessageTemplate(accountId);
```

- O submódulo novo não importa nada do legado (L3).
- A segunda linha fica como está até a milestone da outra capacidade; lá ela vira chamada ao `api/` ou à fachada, ou um evento.
