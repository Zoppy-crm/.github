---
name: e2e-zoppy
description: Regras e padrões para escrever testes E2E Playwright no projeto Zoppy FE. Use ao criar, revisar ou corrigir testes E2E. Foco em independência entre testes, resistência a flaky tests e padrões do projeto.
---

# E2E Zoppy — Regras para Playwright

Padrões obrigatórios para testes E2E no zoppy-FE. Foco em **independência**, **resistência a flaky** e **manutenção**.

## Regra #1 — Cada teste é independente

**Cada `test()` deve funcionar sozinho, sem depender de outro teste ter rodado antes.**

```typescript
// ERRADO — testes acoplados em serial
test.describe.serial('Fluxo', () => {
    test('navegar para a página', async () => {
        /* navega */
    });
    test('verificar conteúdo', async () => {
        /* assume que já navegou */
    });
});

// CORRETO — cada teste navega por conta própria
test.describe('Fluxo', () => {
    test('deve exibir conteúdo na página', async ({ page }) => {
        await page.goto('/dashboard/feature');
        await expect(page.getByTestId('content')).toBeVisible();
    });

    test('deve navegar entre abas', async ({ page }) => {
        await page.goto('/dashboard/feature');
        await page.getByText('Aba 2').click();
        await expect(page).toHaveURL(/\/aba-2/);
    });
});
```

**Exceção:** Use `test.describe.serial` apenas quando testar um fluxo CRUD completo onde cada passo depende do anterior (criar → editar → deletar) e limpar estado entre testes não é viável.

## Regra #2 — Nunca usar `networkidle`

`waitForLoadState('networkidle')` causa flaky tests porque qualquer polling, websocket ou request contínuo impede o estado de ser atingido.

```typescript
// ERRADO — trava se há polling
await page.waitForLoadState('networkidle');

// CORRETO — aguardar o elemento que indica que a página carregou
await page.goto('/dashboard/feature');
await page.getByTestId('feature-content').waitFor({ state: 'visible', timeout: 15000 });
```

## Regra #3 — Seletores por `data-testid`

Usar `data-testid` como seletor primário. Nunca depender de classes CSS, tags HTML ou texto que pode mudar.

```typescript
// CORRETO
await page.getByTestId('provider-list');
await page.getByTestId('sak-card').getByRole('button', { name: 'Configurar' });
await page.getByRole('button', { name: /salvar/i });

// ERRADO — frágil
await page.getByText('Integrações'); // texto pode mudar
await page.locator('.flex.gap-6 > div:nth-child(2) button');
await page.locator('ui-button[type="primary"]');
```

### `getByText` — nunca usar como seletor de interação

`getByText` é frágil: textos mudam com i18n ou redesign. **Sempre usar `data-testid`.**

### Angular `[routerLink]` em `<div>` — precisa de `data-testid`

Elementos com `[routerLink]` em `<div>` **não geram atributo `href`**, portanto não funcionam com `getByRole('link')` nem com `[href]` selector. Adicionar `[attr.data-testid]` no template:

```html
<!-- template Angular -->
<div [routerLink]="item.route" [attr.data-testid]="'menu-item-' + item.id"></div>
```

```typescript
// teste — funciona
const item: Locator = page.getByTestId('menu-item-integrations');
```

### `getByRole('link')` — cuidado com nome acessível

`getByRole('link', { name: 'Texto' })` pode falhar quando o `<a>` contém ícones (`ps-icon`, `mat-icon`) — o nome acessível inclui o texto do ícone concatenado ao label. Preferir `getByTestId`:

```typescript
// ERRADO — falha se <a> contém <ps-icon> junto ao texto
const item = page.getByRole('link', { name: 'Integrações' });

// CORRETO — adicionar data-testid="main-menu-configurations" no template
const item: Locator = page.getByTestId('main-menu-configurations');
```

## Regra #4 — Aguardar antes de agir

Sempre aguardar o elemento estar visível antes de interagir. Usar auto-waiting do Playwright (`.click()`, `.fill()` já aguardam), mas para verificações de estado, usar `waitFor()`.

```typescript
// CORRETO — aguarda o modal antes de verificar conteúdo
await page.getByTestId('sak-card').getByRole('button', { name: 'Configurar' }).click();
await page.locator('.modal-content').waitFor({ state: 'visible', timeout: 5000 });
await expect(page.locator('.modal-content')).toContainText('SAK');

// ERRADO — verifica imediatamente sem aguardar
await page.getByRole('button', { name: 'Configurar' }).click();
await expect(page.locator('.modal-content')).toContainText('SAK'); // pode falhar se modal demora
```

## Regra #5 — Timeouts explícitos e curtos

Não depender do timeout global (120s). Usar timeouts explícitos e curtos para falhar rápido.

```typescript
// CORRETO — timeout explícito
await page.getByTestId('content').waitFor({ state: 'visible', timeout: 10000 });

// ERRADO — depende do timeout global de 120s
await page.getByTestId('content').waitFor({ state: 'visible' });
```

## Regra #6 — Capturar erros de runtime

Testes que validam que uma feature funciona sem erros devem capturar `pageerror`.

```typescript
test('should open modal without runtime errors', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', error => pageErrors.push(error.message));

    await page.goto('/dashboard/feature');
    await page.getByRole('button', { name: 'Abrir' }).click();
    await page.locator('.modal-content').waitFor({ state: 'visible', timeout: 5000 });

    expect(pageErrors).toEqual([]);
});
```

## Regra #7 — Estrutura do projeto E2E

```
e2e/
└── <feature>/
    ├── pages/
    │   └── <feature>.page.ts       # Page Object — locators e ações
    ├── selectors/
    │   └── <feature>.selectors.ts   # data-testid constants
    └── tests/
        └── <feature>-<fluxo>.spec.ts  # Testes agrupados por fluxo
```

## Regra #8 — Page Object sem estado

Page Objects encapsulam **locators e ações**, não estado. Nunca guardar dados de teste no Page Object.

```typescript
// CORRETO
export class IntegrationPage {
    constructor(private readonly page: Page) {}

    async goToIntegrations(tab: string): Promise<void> {
        await this.page.goto(`/dashboard/configurations-v2/new-integration/${tab}`);
        await this.page.getByTestId('provider-list').waitFor({ state: 'visible', timeout: 15000 });
    }
}

// ERRADO — guarda estado
export class IntegrationPage {
    currentTab: string = 'erp'; // NÃO
}
```

## Regra #9 — Contexto isolado por teste

Quando os testes são independentes, usar fixtures do Playwright que criam contexto isolado automaticamente. Não compartilhar `sharedPage` entre testes independentes.

```typescript
// CORRETO — cada teste tem sua própria page
test('deve exibir providers', async ({ page }) => {
    await page.goto('/dashboard/configurations-v2/new-integration/erp');
    // ...
});

// ACEITÁVEL — shared context APENAS para serial
test.describe.serial('CRUD completo', () => {
    let sharedPage: Page;
    test.beforeAll(async ({ browser }) => {
        const context = await browser.newContext({ storageState: 'e2e/fixtures/auth/.auth.json' });
        sharedPage = await context.newPage();
    });
});
```

## Regra #10 — Testes devem ser rápidos

-   Cada teste deve completar em **< 30s** (exceto fluxos CRUD completos)
-   Se um teste demora mais, provavelmente está esperando algo desnecessário
-   Use `timeout` curto para falhar rápido e identificar o problema

## Padrão de autenticação do projeto

```typescript
// Todos os testes E2E dependem do setup de autenticação
// O storageState é gerado pelo auth.setup.ts e reutilizado
// Configurado no playwright.config.ts via project dependencies
```

## Regra #11 — Tipos explícitos em variáveis

Todas as variáveis declaradas em testes devem ter tipo explícito após o nome. Nunca depender de inferência.

```typescript
// CORRETO
const item: Locator = page.getByTestId('menu-item');
const response: Response | null = await page.goto('/dashboard');
const errors: string[] = [];

// ERRADO — lint falha
const item = page.getByTestId('menu-item');
const response = await page.goto('/dashboard');
```

Importar tipos do `@playwright/test` separadamente das fixtures do projeto:

```typescript
import { test, expect } from '../../shared/fixtures';
import type { Locator, Response } from '@playwright/test';
```

---

## Checklist ao criar testes E2E

-   [ ] Cada teste navega para a página por conta própria (`page.goto(...)`)
-   [ ] Nenhum `waitForLoadState('networkidle')`
-   [ ] Seletores usam `data-testid` — nunca `getByText` para interação
-   [ ] Elementos Angular com `[routerLink]` em `<div>` têm `[attr.data-testid]` no template
-   [ ] `getByRole('link')` evitado quando `<a>` contém ícones — usar `getByTestId`
-   [ ] Timeouts explícitos e curtos em `waitFor()`
-   [ ] Page errors capturados quando testando que features não dão erro
-   [ ] Testes podem rodar em qualquer ordem
-   [ ] Testes podem rodar em paralelo sem interferir um no outro
-   [ ] Todas as variáveis com tipo explícito (`const x: Locator = ...`)
