# Vícios de spec que escondem defeito

## Asserção que não distingue certo de errado

- `toBeDefined()`, `toBeTruthy()`, `length > 0` sobre valor que o código calcula: qualquer saída não vazia passa (#9305: seis `toBeDefined` numa lista que vinha duplicada).
- Asserção só no efeito colateral principal quando o método também devolve um valor calculado (#11207: verificava a `customerAction` e nunca o `minimumAmount`).
- Contar o proxy errado: número de queries quando o custo é linhas lidas (#11424).
- Zerar duas entradas no mesmo teste: `phone: null` e `firstName: null` juntos, sem saber qual regra disparou (#11357).

## Fixture que fixa a partição

- Factory que sempre preenche o campo opcional (`wcId` aleatório em todo cupom, #10701).
- Mesmo literal em todo teste (`'31998913655'`, e-mail idêntico no banco e na planilha).
- `as unknown as T` montando objeto que não existe em produção (User sem `companyId`, #10478).

## Mock que esconde

- Stub de lib de provedor com `jest.fn()`: aceita id nulo sem reclamar, a lib real lançaria (#10701).
- Mock de Redis/fila que devolve o objeto pronto, pulando o `JSON.stringify/parse` (#10478).

## Oráculo

- Nome de teste que generaliza a crença: "does not register reimbursement coins" (#11565), "is a stub outside production" (#11406).
- Teste de limite que afirma a recusa sem fonte: `amount 1` "deve ser inválido", mas o nó do workflow aceita R$1 (#8871). O teste existia, estava no limite certo e protegia o bug.
- Comportamento com defeito exercitado e aceito como irrelevante por um comentário no teste (#11357).
