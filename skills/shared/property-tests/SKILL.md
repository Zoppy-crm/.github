---
name: property-tests
description: Use when writing or changing tests for a helper, normalizer, formatter, parser, mapper, price or date calculation, cache/serialization round-trip, or any operation that must be idempotent — "normaliza telefone", "formata", "converte", "mapeia o payload", "roda duas vezes", "teste de propriedade", "fast-check", "property-based".
---

# Testes por propriedade

## Princípio

Teste de exemplo verifica as entradas que alguém lembrou de escrever. Teste de propriedade gera centenas de entradas e verifica uma regra que vale para **todas**. Ele pega exatamente o que escapa na Zoppy: string só com espaços, `NaN`, caixa trocada, `undefined` virando `"undefined"`, segunda execução duplicando, valor que volta diferente do cache.

Não substitui o teste de exemplo. Complementa, onde a função tem uma regra geral.

## Quando usar

- **Sim:** helper, normalizador, formatador, parser, mapper de payload, cálculo de preço, data ou cupom, serialização, operação que roda de novo (sync, backfill, atribuição).
- **Não:** orquestração cujo resultado só faz sentido com um cenário montado à mão. Ali, use teste de exemplo com a skill `test-design`.

## As propriedades

Escolha as que valem para a função. Cada uma é um `it()`.

| Propriedade | Forma | Pega |
|---|---|---|
| **Não quebra** | qualquer entrada do tipo aceito, inclusive `null` e `undefined` se o tipo permite, não lança erro inesperado | TypeError com lista vazia, id nulo |
| **Saída válida** | a saída sempre cumpre o contrato: nunca `"undefined"`/`"null"`, nunca `NaN`, preço ≥ 0, telefone só dígitos | `String(undefined)`, sentinela `0` |
| **Idempotência** | `f(f(x))` é igual a `f(x)` | normalização aplicada duas vezes |
| **Ida e volta** | `ler(gravar(x))` é igual a `x` | data voltando como string do cache |
| **Equivalência** | `f(x)` é igual a `f(variante(x))` quando devem ser iguais: caixa, espaço nas pontas, máscara | e-mail com caixa diferente |
| **Repetir não duplica** | rodar a operação 2 vezes deixa o mesmo estado que 1 vez | atribuição de features duplicando |

## Geradores

Os geradores padrão raramente produzem os valores que quebram. Misture sempre:

```typescript
import fc from 'fast-check';

const textoArriscado = fc.oneof(
    fc.string(),
    fc.constantFrom('', ' ', '   ', '\t', '\n'),
    fc.string().map((s) => `  ${s}  `),
    fc.mixedCase(fc.string())
);
const numeroArriscado = fc.oneof(fc.double(), fc.constantFrom(0, 1, -1, NaN, Infinity, -Infinity));
const opcional = <T>(arb: fc.Arbitrary<T>) => fc.option(arb, { nil: undefined });
```

## Exemplo

```typescript
it('normalizePhone é idempotente e nunca devolve texto que não seja dígito', () => {
    fc.assert(
        fc.property(opcional(textoArriscado), (entrada) => {
            const uma = normalizePhone(entrada);
            expect(normalizePhone(uma)).toEqual(uma);
            expect(uma === null || /^\d*$/.test(uma)).toBe(true);
        })
    );
});
```

Com banco (sync, backfill), use `fc.asyncProperty` com `{ numRuns: 20 }` e limpe o banco a cada execução.

## Quando uma propriedade falha

O fast-check reduz a entrada ao menor contraexemplo. Transforme esse contraexemplo num **teste de exemplo fixo**, com o valor literal. Ele documenta o caso e continua rodando mesmo se o gerador mudar. Se a função foi corrigida por causa dele, é uma linha nova da tabela "Entradas testadas" do PR.

## Setup

`fast-check` ainda não está em nenhum repo da Zoppy. Adicionar como devDependency mexe no `package.json` e no lock: **confirme com o dev antes**, e siga a regra de lock do repo (o `npm i` de alguns repos poda pacotes; confira o diff do lock).
