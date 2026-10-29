---
name: os-http-route
description: >
    Implementa rotas Hono do backend Zoppy OS v2 com DTO Zod, safeParse, sessão por middleware
    e tradução de erro de negócio para HTTP conforme o contrato OpenAPI OS. Use ao criar
    endpoint ou ligar uma operação ao backend real. Triggers: "rota Hono OS", "DTO backend OS",
    "safeParse", "erro HTTP OS", "endpoint OS", "contrato OpenAPI OS".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2, Hono 4.13.14, Zod 4.6.7.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Hono 4.13.14 / Zod 4.6.7 / Bun 1.4.3 / TypeScript 7.0.2"
---

# Rota HTTP do OS

## 1. Comece pelo contrato da operação

Leia `packages/contract/zoppy-os.openapi.yaml`: método, path, parâmetros, corpo, resposta,
status e envelope de erro. Confira o consumidor e o script real de geração de tipos.
Não baixe Swagger do zoppy-api nem copie seu envelope Nest, renovação de sessão ou comandos.
Se faltar resposta de validação/autenticação no YAML, ajuste o contrato na mesma fatia antes de
declarar aderência. Não invente endpoint, status, SSE ou política de erro silenciosamente.

## 2. Mantenha a borda fina

1. DTOs Zod ficam em `entrypoints/http/<assunto>/dto.ts`; rotas, em `routes.ts`.
2. Leia JSON como `unknown`, capture JSON malformado e use `safeParse`. Valide também path/query.
   Use `.strict()` quando o contrato recusar campos extras; normalize só conforme o contrato.
3. Registre o middleware de sessão antes das rotas protegidas; ele resolve a identidade por porta,
   guarda um principal interno tipado e recusa sessão ausente. Veja `os-auth-session`.
4. Passe dados validados e principal ao caso de uso injetado. Tenant/pessoa não vêm do DTO.
5. Faça o mapper de resultado e erro na borda. Domínio/aplicação retornam valores tipados;
   não conhecem `Response`, Hono ou status HTTP.

Trecho mínimo do ensaio para parsing; `/proof` e seu envelope são apenas demonstração,
não uma operação do contrato OS. Sessão e caso de uso devem ser ligados na rota de produto.

```typescript
import { Hono } from "hono";
import { z } from "zod";

const input = z.object({ value: z.string().trim().min(1).max(80) }).strict();

export function createProofApi() {
    return new Hono().post("/proof", async (context) => {
        const body: unknown = await context.req.json().catch(() => undefined);
        const parsed = input.safeParse(body);
        if (!parsed.success) return context.json({ errorType: "invalid_input" }, 400);
        return context.json({ value: parsed.data.value }, 201);
    });
}
```

## 3. Traduza erros pelo tipo

Faça `switch` exaustivo no discriminante do erro de negócio e retorne o status/envelope daquela
operação no YAML. Não decida por `error.message`; não devolva detalhes de SQL, stack ou conteúdo
privado. Erro técnico inesperado recebe resposta genérica do contrato e correlação interna.

401 para sessão ausente, 403 para proibição, 404 para recurso oculto/inexistente e 409 para conflito
são possibilidades a conferir no contrato, não um mapa universal desta skill. Não importar `HTTPException`
na aplicação nem transformar toda falha em 400. O mapper preserva a chave de erro estável do contrato.

## 4. Verifique o comportamento

Use `bun test` e `app.request(...)` para atravessar middleware, parsing, caso de uso e mapper.
Cubra sucesso, JSON malformado, campo inválido/extra conforme YAML, sessão ausente, pessoa pendente,
recusa de acesso e erro de negócio pertinente. Confira corpo e status contra o contrato,
inclusive campos omitidos por privacidade. Teste com porta falsa não demonstra RLS nem OAuth real.
Nomes em inglês snake_case, como `rejects_malformed_json_without_exposing_internal_error`.

## Anti-padrões

- Fazer cast do body para DTO, usar `parse` sem tratamento ou aceitar tenant/executor do cliente.
- Rota instanciando repositório, abrindo SQL ou importando adaptador concreto.
- Reutilizar modelo Drizzle/grafo como resposta pública ou deixar SDK escolher erro HTTP.
- Afirmar backend integrado porque o MSW ou a rota `/proof` passa.

Leia [fontes e limites](references/fontes.md) para as APIs usadas no exemplo.
