---
name: os-auth-session
description: >
    Integra Better Auth ao backend Zoppy OS v2 com Drizzle, login Google e sessão, mapeando
    autenticação para pessoa, times e capacidades internos. Use ao configurar login,
    middleware de sessão ou resolução de principal. Triggers: "Better Auth OS", "login Google OS",
    "sessão OS", "pessoa pendente", "principal OS", "Master OS".
compatibility: Zoppy OS v2; Bun 1.4.3, Better Auth 1.7.14, Drizzle 0.45.4 e Hono 4.13.14.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Better Auth 1.7.14 / Drizzle ORM 0.45.4 / Hono 4.13.14 / Google OAuth"
---

# Autenticação e sessão do OS

## 1. Configure o adaptador, não a identidade do produto

Em `adapters/auth/better-auth.ts`, monte Better Auth com o schema explícito de auth, criado
em `db/schema/auth.ts`, e `drizzleAdapter(db, { provider: "pg", schema })`.
Não basta apontar para um schema de negócio sem `user`, `session`, `account` e `verification`.

Exemplo de configuração; `db`, `schema` e `env` são dependências da composição e env já validado:

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";

const auth = betterAuth({
    baseURL: env.authBaseUrl,
    basePath: "/api/auth",
    secret: env.authSecret,
    database: drizzleAdapter(db, { provider: "pg", schema }),
    trustedOrigins: env.trustedOrigins,
    advanced: {
        useSecureCookies: !env.isDevelopment,
        defaultCookieAttributes: {
            httpOnly: true,
            secure: !env.isDevelopment,
            sameSite: "lax",
        },
    },
    session: { cookieCache: { enabled: false } },
    account: { encryptOAuthTokens: true },
    socialProviders: {
        google: {
            clientId: env.googleClientId,
            clientSecret: env.googleClientSecret,
        },
    },
    telemetry: { enabled: false },
});
```

Configure no Google o callback correspondente ao domínio/basePath, por exemplo
`https://<dominio>/api/auth/callback/google`. Segredos ficam em configuração validada, nunca em
DTO, código ou log. A entrada de auth encaminha o `Request` ao `auth.handler(request)`;
a composição injeta essa função. Não bloqueie login/callback com o middleware que exige sessão.

`trustedOrigins` é lista validada de origens exatas aprovadas; fora de dev não aceite localhost,
curingas ou HTTP. Cookies são httpOnly, Secure fora de dev e SameSite Lax. Não habilite
`disableCSRFCheck` nem `disableOriginCheck`. `session.cookieCache` fica desligado por padrão:
ligado, uma sessão revogada pode continuar válida até expirar o cache (`maxAge`); qualquer mudança
exige decisão explícita sobre essa janela e teste de revogação.
`account.encryptOAuthTokens: true` cifra access/refresh tokens; **na 1.7.14 o `idToken` não é cifrado**
pelo fluxo OAuth. Trate-o como segredo persistido, restrinja acesso ao adaptador e não prometa
cifragem integral. A documentação atual é genérica; prevalece o código fixado (veja fontes).
Restrição de domínio de e-mail, quando exigida, vem de configuração validada, nunca domínio fixo
no código. Valide a identidade verificada pelo provedor; um domínio não concede capacidades.

## 2. Resolva sessão por porta e middleware

1. O adaptador consulta `auth.api.getSession({ headers, returnHeaders: true })` com headers reais.
   Traduza `response` para identidade interna e retorne cada `headers.getSetCookie()` pela porta
   de sessão; o middleware usa `context.header("Set-Cookie", cookie, { append: true })`, inclusive
   nas recusas. Não una cookies por vírgula nem os perca ao renovar/limpar a sessão.
2. Sessão ausente retorna `null`; sessão expirada/revogada não vira principal por fallback.
3. O caso de uso de identidade mapeia o identificador autenticado à pessoa interna,
   times e capacidades atuais. Pessoa pendente não recebe capacidades de pessoa ativa.
4. O middleware protegido recebe essa resolução por porta e coloca somente o principal interno
   tipado no contexto Hono. Nunca exporte o tipo de sessão Better Auth para domínio/aplicação.

Veja [middleware tipado](references/middleware.md) ao implementar a borda. A recusa de pessoa
pendente e os status/envelopes devem seguir a operação em `packages/contract/zoppy-os.openapi.yaml`.

## 3. Mantenha a autoridade na aplicação

- **Owner/admin do Better Auth não vira Master.** A atribuição de capacidades Zoppy é regra explícita
  da aplicação. Não use nome de papel da biblioteca como atalho de ACL.
- A aplicação é a fonte única de membership de times e capacidades. O OS tem uma organização só;
  não instale o plugin de organização do Better Auth nem mantenha listas concorrentes de membros.
- Body, prompt, thread, headers arbitrários de identidade e parâmetros do SDK não definem executor.
  Referência a recurso enviada pelo cliente deve ser autorizada contra o principal autenticado.
- Jobs usam vínculo de execução guardado no servidor e revalidam identidade/admissão ao consumir.
  Retomada também revalida pessoa ativa, acesso, contas e limite atual.
- Master/gestor recebe somente agregados autorizados; papel administrativo não abre conversa privada.

## 4. Separe login de integração

Login Google autentica; não concede acesso Gmail/Drive. Contas conectadas, escopos e consentimento
de ferramentas são fluxos separados com autorização do produto. Não solicite escopos de Drive/Gmail
só para implementar login. Delegação permanece pendente: não empreste a identidade do dono da agenda.

## 5. Limite acesso ao armazenamento de auth

Migração como `os_owner`, runtime como `os_app` sem DDL ou ownership. Conceda `USAGE` no schema
e grants por nome físico das **quatro** tabelas do Better Auth: `user`, `session`, `account` e
`verification`. Para login Google/sessão: `SELECT/INSERT/UPDATE` em `user` e `account`;
`SELECT/INSERT/UPDATE/DELETE` em `session`; `SELECT/INSERT/DELETE` em `verification` para
criar/consumir/limpar estado OAuth. Se um fluxo habilitado usar update de verification ou delete
de user/account, acrescente somente esse grant após prova de integração; não habilite endpoints
que dependam de permissões ausentes. Restrinja colunas quando compatível com o adaptador fixado.
Sem `GRANT ALL`, grants globais, DDL ou acesso a tabelas de auth por repositórios de negócio.
A resolução consulta auth pelo adaptador e membership por porta da aplicação; worker consulta
vínculo persistido por caso de uso. Não existe bootstrap privilegiado de identidade.

## 6. Proteja rotas do produto

A proteção Better Auth cobre `/api/auth/*`, não as rotas do produto. Nelas, monte `csrf()` de
`hono/csrf` para corpos de formulário **e** guarda de Origin em todo método inseguro (qualquer um
fora de GET/HEAD/OPTIONS), incluindo JSON. Exija Origin exata da lista validada; recuse origem
ausente, `null` ou não aprovada nas rotas autenticadas por cookie. CORS não substitui essa guarda.
Se necessário, monte `cors` de `hono/cors` com origens exatas da configuração e `credentials: true`, nunca `*`. Rotas JSON
mutáveis exigem `Content-Type: application/json` antes de ler o corpo; `req.json()` sozinho
não impede JSON enviado como `text/plain`. Não aplique a guarda do produto ao callback OAuth.
Veja `os-http-route` e o middleware de referência.

## 7. Verifique o que foi implementado

Teste sessão ausente e principal recusado na borda; sessão válida, revogação, pessoa pendente/ativa,
membership de times e não promoção de owner/admin na identidade. Integração real de Google precisa
de prova própria de callback/cookies/sessão; o ensaio só confirmou adaptador Drizzle e sessão ausente.
Não declare login completo validado por `getSession` retornar `null`. Cubra renovação e cada
Set-Cookie, limpeza de cookie revogado, flags, grants como `os_app`, Origin ausente/nula/hostil
em POST/PUT/PATCH/DELETE, JSON com tipo errado e CORS exata sem curinga.

## Anti-padrões

- Identidade do body/prompt/thread ou um `userId` cliente substituindo sessão.
- Autorizar por email do body, papel owner/admin da biblioteca ou simples existência do cookie.
- Expor tokens Google/sessão em resposta de negócio ou persistir memberships contraditórias.
- Usar login Google como consentimento de ferramentas ou tornar pendente ativo automaticamente.

Consulte [fontes e limites](references/fontes.md) ao alterar configuração ou chamadas de sessão.
