# Middleware de sessão na borda

`Principal` e `SessionResolver` são contratos internos mínimos. A resolução mapeia a sessão para
pessoa ativa e permissões atuais da aplicação. `null` é sessão ausente neste exemplo; preserve
recusas tipadas de pessoa pendente na implementação e mapeie-as pelo contrato. A porta de sessão
transporta cookies como strings de resposta, sem expor tipos Better Auth ou Headers ao domínio.

```typescript
import { Hono } from "hono";
import { createMiddleware } from "hono/factory";
import { csrf } from "hono/csrf";
import { cors } from "hono/cors";

type Principal = { readonly personId: string };
type SessionResolver = {
    resolve(headers: Headers): Promise<{
        readonly principal: Principal | null;
        readonly setCookies: readonly string[];
    }>;
};
type SessionEnv = { Variables: { principal: Principal } };

export function createProtectedApi(sessions: SessionResolver, approvedOrigins: string[]) {
    const app = new Hono<SessionEnv>();
    app.use(cors({ origin: approvedOrigins, credentials: true }));
    app.use(csrf({ origin: approvedOrigins }));
    app.use(createMiddleware<SessionEnv>(async (context, next) => {
        if (!["GET", "HEAD", "OPTIONS"].includes(context.req.method)) {
            const origin = context.req.header("Origin");
            if (!origin || origin === "null" || !approvedOrigins.includes(origin)) {
                return context.json({ errorType: "origin_not_allowed" }, 403);
            }
        }
        await next();
    }));
    app.use(createMiddleware<SessionEnv>(async (context, next) => {
        const { principal, setCookies } = await sessions.resolve(context.req.raw.headers);
        for (const cookie of setCookies) context.header("Set-Cookie", cookie, { append: true });
        if (principal === null) return context.json({ errorType: "unauthenticated" }, 401);
        context.set("principal", principal);
        await next();
    }));
    return app;
}
```

`approvedOrigins` vem de configuração validada, não vazia, com origens exatas e HTTPS fora de dev,
sem localhost em produção nem curingas. A composição registra as rotas de produto nessa instância;
elas leem `context.get("principal")`. As rotas de auth usam outra montagem para preservar login e
callback. Envelopes/status de exemplo precisam existir no YAML antes de adoção. Mapeie também
as recusas lançadas por `csrf()` no tradutor HTTP para não devolver envelope estranho ao contrato.
Não declare variáveis globais Hono como se esse middleware já tivesse rodado em todas as rotas.

`csrf()` protege tipos de formulário, não JSON; a guarda de Origin acima cobre **todo método
inseguro**, também JSON. Nas operações cujo corpo contratual é JSON, valide media type
`application/json` (com parâmetros válidos) **antes** de `req.json()`, recusando texto/formulário.
CORS com credenciais usa somente origens exatas e não substitui a guarda de Origin.

No adaptador Better Auth:

```typescript
const { response: session, headers: responseHeaders } = await auth.api.getSession({
    headers,
    returnHeaders: true,
});
const setCookies = responseHeaders.getSetCookie();
```

Mapeie `session` para identidade da aplicação por porta e devolva `{ principal, setCookies }`,
inclusive com sessão ausente/revogada e recusa tipada, para renovar/limpar cookies na borda.
Não una Set-Cookie com vírgula ou sobrescreva os anteriores. Não coloque sessão bruta, token ou
headers no principal. Revogação é consultada no banco com `session.cookieCache.enabled: false`.
Teste cookies múltiplos em sucesso/recusa e renovação ao atingir `updateAge`.
