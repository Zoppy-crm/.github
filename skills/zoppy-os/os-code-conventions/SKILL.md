---
name: os-code-conventions
description: >
    Aplica convenções de código do backend Bun/TypeScript do Zoppy OS v2: TS7 estrito, ESM,
    nomes em inglês, erros tipados, código sem comentários/docstrings e dinheiro decimal.
    Use ao implementar ou revisar código backend. Triggers: "convenções backend OS", "TypeScript 7 OS",
    "skipLibCheck", "erro de negócio tipado", "ESM OS", "code style OS".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2 e ESM.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Bun 1.4.3 / TypeScript 7.0.2 / ESM / decimal.js / PostgreSQL numeric"
---

# Convenções do backend OS

## 1. Use o checker e o runtime fixados

Backend somente Bun/TypeScript. `package.json` usa `"type": "module"`; fixe versões e lock,
sem overrides para esconder incompatibilidades. A base validada usa Bun 1.4.3, TS 7.0.2,
Hono 4.13.14, Zod 4.6.7, Better Auth 1.7.14, drizzle-orm 0.45.4, drizzle-kit 0.31.11,
pg-boss 12.38.0, deepagents 1.16.0, `@langchain/core` 1.2.14 e `@langchain/langgraph` 1.4.10.
Não atualize um peer isolado por ver uma versão mais recente em documentação.

Configuração derivada do ensaio, removendo DOM para o backend e ajustando `include`:

```json
{
    "compilerOptions": {
        "target": "ES2023",
        "module": "ESNext",
        "moduleResolution": "Bundler",
        "lib": ["ES2023"],
        "types": ["bun"],
        "strict": true,
        "exactOptionalPropertyTypes": true,
        "noUncheckedIndexedAccess": true,
        "verbatimModuleSyntax": true,
        "allowImportingTsExtensions": true,
        "noEmit": true,
        "skipLibCheck": true
    },
    "include": ["src/**/*.ts", "db/**/*.ts", "tests/**/*.ts", "drizzle.config.ts"]
}
```

`types: ["bun"]` fornece as APIs do runtime; não adicione `lib DOM` para habilitar `window` ou
`document` no servidor. O frontend usa seu próprio tsconfig. Verifique a configuração no checker fixado.

**Limite conhecido:** o typecheck do código do ensaio passa. Com `skipLibCheck: false`, há cerca de
100 erros nas declarações publicadas de LangChain, pg-boss e Drizzle. Por isso a base usa
`skipLibCheck: true`, sem remendo de declaração, supressão ou override. Isso não corrige os tipos
das bibliotecas nem significa aprovação integral delas. Verifique separadamente tipos públicos
consumidos e inferências que escapem como `any`; não afrouxe o código autoral.

## 2. Escreva tipos que expressem a regra

1. Sem `any`, `@ts-ignore` ou cast duplo para silenciar erro. Entrada desconhecida é `unknown`,
   seguida de validação/narrowing. Não use `@ts-expect-error` para contornar tipagem do produto.
2. `exactOptionalPropertyTypes`: omita campo opcional ausente; não atribua `undefined` sem o tipo
   permitir explicitamente. `noUncheckedIndexedAccess`: trate item ausente, sem `!` para esconder risco.
3. Use `import type` para tipos e imports ESM. Arquivos TS locais podem usar extensão `.ts` conforme
   o ensaio; não introduza `require`/CommonJS ou aliases sem configuração real.
4. Interfaces de porta não carregam Context Hono, sessão Better Auth, builder Drizzle ou mensagens SDK.

## 3. Nomeie e organize com clareza

Identificadores em inglês: camelCase para valores/funções, PascalCase para tipos/classes e
kebab-case para arquivos. Nomes de teste em inglês snake_case descrevem comportamento.
**Zero comentários e docstrings no código**, inclusive JSDoc e anotações explicativas inline.
Intenção deve aparecer em nomes, tipos e funções pequenas. Explicação de decisão vai em Markdown;
não injete comentário em código para compensar abstração pouco clara.

## 4. Retorne erros de negócio como valores tipados

Use união discriminada; a borda mapeia para o contrato HTTP. Exceção representa falha técnica,
não fluxo normal de pessoa pendente, acesso negado ou conflito de regra.

```typescript
type AdmissionResult =
    | { readonly ok: true; readonly executionId: string }
    | { readonly ok: false; readonly error: "person_pending" | "access_denied" };

function getExecutionId(result: AdmissionResult): string | null {
    if (!result.ok) return null;
    return result.executionId;
}
```

Não lance status/Response no domínio e não decida por texto de erro. Se a UoW precisar rollback
após uma recusa tipada, traduza internamente para mecanismo controlado e capture fora da transação;
retornar `{ ok: false }` sozinho não faz Drizzle reverter alterações.

## 5. Não represente dinheiro como number

Preço, débito, budget e custo usam PostgreSQL `numeric`, decimal.js no cálculo e string decimal
nos limites de transporte. Proibidos `Number`, `parseFloat`, coerção unária e `.toNumber()` nesse
fluxo. Não fixe precisão, reserva concorrente ou overshoot sem decisão aprovada. Veja `os-persistence`.

## 6. Nada hardcoded

Regra de negócio configurável, texto de instrução de agente, IDs, domínios, listas de pessoas e URLs
vêm de configuração validada ou de dado do catálogo, nunca de constante no código. Receba esses
valores por dependências tipadas, valide na composição e recuse configuração ausente/inválida.
Não esconda decisão pendente em default, prompt inline ou lista fixa de usuários. Literais técnicos
de protocolo e fixtures determinísticas são permitidos; não os promova a configuração de produção.

## 7. Confira o resultado

Rode o checker TS7 instalado (`tsc --version` e `tsc --noEmit` pelo script real do pacote),
`bun test` para as suítes pertinentes e verificações de arquitetura. Não declare typecheck verde
só porque Bun executa TS. Não invente regra de retenção, destino de telemetria, delegação ou política
temporal para preencher uma lacuna durante refactor.

## Anti-padrões

- `any` indireto de API pública, supressão de erro, patch de `.d.ts` ou override de peers.
- Desativar `strict`/`exactOptionalPropertyTypes`/`noUncheckedIndexedAccess` por SDK incompatível.
- Comentário/JSDoc explicando código, identificador em português ou erro de negócio lançado como HTTP.
- Saldo em `number`, defaults de política pendente ou declarar bibliotecas integralmente verificadas.

Consulte [fontes e limites](references/fontes.md) ao revisar versões e a ressalva de tipos.
