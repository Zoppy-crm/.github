# Middleware de sessão na borda

`Principal` e `SessionResolver` abaixo são contratos internos mínimos de exemplo; o domínio
real acrescenta os tipos/capacidades da fatia. A resolução já mapeia a sessão Better Auth para
pessoa ativa e escopo atual. `null` representa sessão ausente neste exemplo; a implementação
real deve preservar recusas tipadas de pessoa pendente e mapeá-las conforme o contrato.

```typescript
import { Hono } from "hono";
import { createMiddleware } from "hono/factory";

type Principal = {
    readonly personId: string;
    readonly tenantId: string;
};
type SessionResolver = {
    resolve(headers: Headers): Promise<Principal | null>;
};
type SessionEnv = { Variables: { principal: Principal } };

export function createProtectedApi(sessions: SessionResolver) {
    const requireSession = createMiddleware<SessionEnv>(async (context, next) => {
        const principal = await sessions.resolve(context.req.raw.headers);
        if (principal === null) return context.json({ errorType: "unauthenticated" }, 401);
        context.set("principal", principal);
        await next();
    });
    const app = new Hono<SessionEnv>();
    app.use(requireSession);
    return app;
}
```

A composição registra as rotas protegidas nessa instância; elas leem `context.get("principal")`.
As rotas públicas de auth usam outra montagem. O 401/envelope ilustrativo precisa existir no YAML
da operação antes de ser adotado. Não declare variáveis globais Hono como se o middleware já tivesse
rodado em toda rota: tipo não prova ordem de montagem.

No adaptador Better Auth, a consulta validada é:

```typescript
const session = await auth.api.getSession({ headers });
```

Depois traduza o identificador autenticado para a identidade da aplicação por porta. Não coloque
sessão bruta, token ou headers no principal e não derive tenant de um header arbitrário do cliente.
