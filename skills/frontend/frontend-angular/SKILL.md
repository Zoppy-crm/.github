---
name: frontend-angular
description: Regras e padrões para desenvolvimento frontend em Angular nos projetos da Zoppy. Use este guia ao criar, revisar ou corrigir código Angular. Cobre arquitetura, estrutura de pastas, convenções de código, uso do design system e padrões de teste.
---

# Frontend Angular — Boas Práticas

Convenções e padrões para desenvolvimento frontend nos projetos Angular da Zoppy (zoppy-FE, zoppy-partners-fe e outros).

## Stack

- **Angular**: 19+ (standalone components, signals, new control flow)
- **TypeScript**: 5.5+
- **Styling**: Tailwind CSS com preset `@Zoppy-crm/tailwind`
- **Design System**: `ui-components` (monorepo com 45+ packages `@Zoppy-crm/*`)
- **Testes**: Jasmine + Karma (unit), Playwright (e2e)
- **Build**: Angular CLI + ng-packagr (para libraries)

---

## Componentes

### Standalone obrigatório

Todos os componentes devem ser `standalone: true`. Não criar NgModules.

```typescript
@Component({
    selector: 'app-feature',
    standalone: true,
    imports: [CommonModule, UiButtonComponent, UiInputComponent],
    templateUrl: './feature.component.html'
})
export class FeatureComponent {}
```

### Signals como padrão

Usar Angular Signals para estado de componente. Evitar `@Input()` / `@Output()` decorators — usar a API funcional.

Sempre declarar o tipo explicitamente após a variável — não depender de inferência do TypeScript para signals, inputs e outputs. Isso torna o tipo visível sem precisar inspecionar o valor inicial, e evita surpresas quando o tipo inferido não é o esperado.

```typescript
// CORRETO — Signals API com tipagem explícita
export class FeatureComponent {
    // Inputs
    title: InputSignal<string> = input.required<string>();
    description: InputSignal<string> = input<string>('');

    // Outputs
    saved: OutputEmitterRef<void> = output<void>();
    deleted: OutputEmitterRef<string> = output<string>();

    // Estado local
    loading: WritableSignal<boolean> = signal(false);
    items: WritableSignal<Item[]> = signal<Item[]>([]);

    // Estado derivado
    hasItems: Signal<boolean> = computed(() => this.items().length > 0);
    filteredItems: Signal<Item[]> = computed(() => this.items().filter(i => !i.archived));
}
```

```typescript
// EVITAR — decorators legados
export class FeatureComponent {
    @Input() title!: string;
    @Output() saved = new EventEmitter<void>();
}
```

### Change Detection

Usar `ChangeDetectionStrategy.OnPush` em componentes novos. Signals garantem que o Angular detecta mudanças corretamente com OnPush.

```typescript
@Component({
    selector: 'app-feature',
    standalone: true,
    changeDetection: ChangeDetectionStrategy.OnPush,
    ...
})
```

### Control Flow

Usar o novo control flow (`@if`, `@for`, `@switch`) ao invés de diretivas estruturais (`*ngIf`, `*ngFor`, `ngSwitch`).

```html
<!-- CORRETO -->
@if (loading()) {
<app-skeleton />
} @else { @for (item of items(); track item.id) {
<app-item-card [item]="item" />
} } @switch (status()) { @case ('active') { <ui-tag-pill variant="success">Ativo</ui-tag-pill> } @case ('inactive') {
<ui-tag-pill variant="warning">Inativo</ui-tag-pill> } }
```

```html
<!-- EVITAR -->
<app-skeleton *ngIf="loading"></app-skeleton>
<app-item-card *ngFor="let item of items" [item]="item"></app-item-card>
```

### Componentes Inteligentes

Todos os componentes podem injetar services — state services, API services, ou qualquer serviço compartilhado. Não há restrição de injeção por nível hierárquico.

- **Container (page)**: coordena navegação e ciclo de vida da feature; provê o feature state service via `providers: [FeatureStateService]`
- **Sub-components**: injetam o state service e/ou outros services (incluindo `ApiService`) diretamente — sem prop drilling
- Use `input()` / `output()` quando o dado vem de **fora do escopo da feature** (ex: componentes reutilizáveis do design system)

```
pages/
└── customers/
    ├── customers.component.ts          # Container — provê CustomersStateService
    └── components/
        ├── customer-card.component.ts   # Injeta CustomersStateService diretamente
        └── customer-filters.component.ts # Injeta CustomersStateService diretamente
```

---

## Schema-Driven UI

Para telas de dados dinâmicos (dashboards, relatórios, listagens configuráveis), adotar o padrão **schema-driven** onde o backend define a estrutura e o frontend apenas renderiza.

### Princípio

O frontend deve ser o mais "burro" possível. Adicionar uma nova seção, card ou coluna deve ser **apenas uma alteração no backend** — zero mudança no frontend.

### Como funciona

1. O backend retorna um **schema** com metadados de renderização (tipo, formato, visibilidade)
2. O frontend tem componentes genéricos que interpretam o schema via `@switch (item.type)`
3. Novas seções/itens aparecem automaticamente quando o backend os inclui no response

### Schema de Card (referência: intelligence-reports)

```typescript
export interface SchemaCard {
    displayName?: string;
    information?: string;
    value: number | string | Date | string[];
    type: 'currency' | 'percentage' | 'number' | 'date' | 'times' | 'text' | 'array';
    typeUnit?: string;
    isHidden?: boolean;
    childCard?: SchemaCard; // Cards aninhados
    tag?: { text: string; type: 'critical' | 'warning' };
    periodComparison?: number;
    comparisonData?: {
        type: 'percentage_of_total' | 'percentage_gap' | 'currency';
        value: number;
    };
}

export interface SchemaSection {
    sectionName: string | string[];
    description?: string;
    cards: SchemaCard[];
}

export interface SchemaChart {
    title?: string;
    description?: string;
    labels: string[];
    datasets: {
        values: any[];
        name?: string;
        type: 'currency' | 'percentage' | 'number' | 'date';
        format?: 'line' | 'bar';
        side?: 'left' | 'right';
        color?: string;
    }[];
}

export interface SchemaTable {
    sectionName: string;
    headers: { id: string; title: string; description: string }[];
    rows: { cells: SchemaCard[]; visible: boolean }[];
}
```

### Componente genérico de renderização

```typescript
@Component({
    selector: 'card-value',
    standalone: true,
    imports: [CurrencyPipe, PercentPipe, RoundPipe, DateMaskPipe],
    template: `
        @switch (card().type) {
            @case ('currency') {
                <ui-text>{{ value() | zoppyCurrency }}</ui-text>
            }
            @case ('percentage') {
                <ui-text>{{ value() | zoppyPercent }}</ui-text>
            }
            @case ('number') {
                <ui-text>{{ value() | zoppyRound }}</ui-text>
            }
            @case ('date') {
                <ui-text>{{ value() | zoppyDateMask: 'DD/MM/YYYY' }}</ui-text>
            }
            @default {
                <ui-text>{{ value() }}</ui-text>
            }
        }
    `
})
export class CardValueComponent {
    card = input.required<SchemaCard>();
    value = computed(() => this.card().value);
}
```

### Quando usar

- Dashboards e relatórios
- Telas de listagem com colunas configuráveis
- Cards de métricas
- Qualquer UI onde a estrutura pode mudar sem deploy de frontend

### Quando NÃO usar

- Formulários complexos com validação client-side
- Fluxos com interação pesada (drag & drop, workflow editor)
- Telas com lógica de UI que o backend não conhece

---

## Services

### Escopo dos Services

**Services globais** (`providedIn: 'root'`): API services, services compartilhados entre features. São singletons na aplicação inteira.

```typescript
@Injectable({ providedIn: 'root' })
export class CustomerService extends ApiService {
    // ...
}
```

**Feature state services** (sem `providedIn`): declarados em `providers` do container para criar uma instância scoped que é destruída junto com o componente.

```typescript
// Sem providedIn — instância scoped
@Injectable()
export class CustomersStateService { ... }

// Declarado no container
@Component({ providers: [CustomersStateService] })
export class CustomersComponent { ... }
```

### API Services

Services que comunicam com a API devem estender `ApiService` e usar signals para armazenar estado.

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureService extends ApiService {
    // Estado como signals
    items = signal<Item[]>([]);
    loading = signal(false);

    loadItems(request: FeatureRequest) {
        this.loading.set(true);
        this.post<Item[], FeatureRequest>(`${this.url}/items`, request)
            .pipe(finalize(() => this.loading.set(false)))
            .subscribe({
                next: response => this.items.set(response),
                error: error => this.toast.error(error.message)
            });
    }
}
```

### Modais via ModalService

Componentes renderizados dentro do `ModalService` **não devem adicionar padding** ao container raiz — o `modal-content` wrapper do ModalService já fornece padding por padrão.

```html
<!-- CORRETO — sem padding no componente do modal -->
<div class="w-[480px] bg-white rounded-3xl flex flex-col gap-6">...</div>

<!-- ERRADO — padding duplicado -->
<div class="w-[480px] p-6 bg-white rounded-3xl flex flex-col gap-6">...</div>
```

### Estado reativo entre componentes

Para estado compartilhado entre componentes que não têm relação pai-filho, usar services com signals. Evitar `BehaviorSubject` em código novo — preferir signals.

```typescript
// CORRETO — Signal-based
@Injectable({ providedIn: 'root' })
export class SidebarService {
    expanded = signal(false);
    toggle() {
        this.expanded.update(v => !v);
    }
}

// EVITAR em código novo — BehaviorSubject
@Injectable({ providedIn: 'root' })
export class SidebarService {
    private _expanded = new BehaviorSubject(false);
    expanded$ = this._expanded.asObservable();
}
```

---

## Styling

### Tailwind como padrão

Usar Tailwind para estilização. Não criar SCSS/CSS customizado exceto para casos que Tailwind não cobre (animações complexas, third-party overrides).

### Utility `cn()` para classes condicionais

Usar `cn()` do `@Zoppy-crm/visual-identity` para compor classes Tailwind. Combina `clsx` + `tailwind-merge`.

```typescript
import { cn } from '@Zoppy-crm/visual-identity';

// Merge seguro de classes Tailwind
const classes = cn(
    'flex items-center gap-2 rounded-lg p-4',
    isActive && 'bg-primary-100 border-primary-500',
    isDisabled && 'opacity-50 cursor-not-allowed',
    className // prop do componente
);
```

### Design tokens

Usar os tokens do preset `@Zoppy-crm/tailwind`. Não hardcodar cores.

```html
<!-- CORRETO — tokens do design system -->
<div class="bg-surface-primary text-text-primary border-border-default">
    <span class="text-critical">Erro</span>
    <span class="text-success">Sucesso</span>

    <!-- EVITAR — cores hardcoded -->
    <div style="background: #f5f5f5; color: #333; border: 1px solid #ddd">
        <span style="color: red">Erro</span>
    </div>
</div>
```

### Responsividade

Usar breakpoints do Tailwind (`sm:`, `md:`, `lg:`). Mobile-first.

```html
<div class="flex flex-col gap-2 md:flex-row md:gap-4 lg:gap-6">
    <!-- ... -->
</div>
```

---

## Design System — ui-components

### Quando usar

**Sempre** que um componente `@Zoppy-crm/*` existir para o caso de uso. Antes de criar um componente local, verificar se já existe no `ui-components`.

Componentes disponíveis: `ui-button`, `ui-input`, `ui-dropdown`, `ui-selector`, `ui-multi-select`, `ui-datepicker`, `ui-timepicker`, `ui-toast`, `ui-text`, `ui-tag-pill`, `ui-label`, `ui-tab`, `ui-progress`, `ui-info-alert`, `icon`, `tooltip`, `skeleton`, `pagination`, `stepper`, `confirm-action`, `switch`, `checkbox`, `radio-button`, `search-bar`, `infinite-scroll`, entre outros.

```typescript
// CORRETO — usar design system
import { UiButtonComponent } from '@Zoppy-crm/ui-button';
import { UiInputComponent } from '@Zoppy-crm/ui-input';
import { UiDropdownComponent } from '@Zoppy-crm/ui-dropdown';
```

### `ui-button` — uso correto

O `<ui-button>` usa `text` como atributo, `(onClick)` para eventos e valores em **lowercase**. Nunca usar conteúdo entre tags para o texto, nem capitalizar os valores de `type`/`size`.

```html
<!-- CORRETO -->
<ui-button type="primary" size="medium" text="Salvar" (onClick)="save()"></ui-button>
<ui-button type="unfocus" size="small" text="Cancelar" (onClick)="cancel()"></ui-button>
<ui-button type="critical" size="medium" text="Excluir" (onClick)="delete()"></ui-button>
<ui-button type="primary" category="secondary" size="medium" text="Voltar" (onClick)="back()"></ui-button>
<ui-button type="primary" size="medium" text="Adicionar" icon="icon-add" [iconBefore]="true" (onClick)="add()"></ui-button>
<ui-button type="unfocus" size="medium" text="Salvar" [wide]="true" [loading]="saving()" (onClick)="save()"></ui-button>

<!-- ERRADO -->
<ui-button type="Unfocus" size="Small" iconBefore="true">Ver tutorial</ui-button>
```

Atributos disponíveis:

| Atributo       | Valores                                        | Notas                                                |
| -------------- | ---------------------------------------------- | ---------------------------------------------------- |
| `text`         | string                                         | Texto do botão — **sempre atributo, nunca conteúdo** |
| `type`         | `"primary"` `"unfocus"` `"critical"`           | **Sempre lowercase**                                 |
| `size`         | `"small"` `"medium"` `"large"`                 | **Sempre lowercase**                                 |
| `category`     | `"default"` `"secondary"` `"link"` `"outline"` | Variante visual                                      |
| `[wide]`       | `true` `false`                                 | Binding — ocupa 100% da largura                      |
| `icon`         | `"icon-add"` `"icon-upload"` etc               | Nome do ícone                                        |
| `[iconBefore]` | `true` `false`                                 | Binding — ícone antes do texto                       |
| `(onClick)`    | handler                                        | Evento customizado do componente                     |
| `[loading]`    | signal/boolean                                 | Estado de carregamento                               |
| `[disabled]`   | signal/boolean                                 | Estado desabilitado                                  |
| `view`         | `"mobile"` `"desktop"`                         | Visibilidade responsiva                              |
| `class`        | Tailwind classes                               | Usa `class` normal (não `className`)                 |

### `ui-text` — uso correto

O `<ui-text>` exige três atributos: `htmlTag`, `type` e `className`. Nunca usar `class` — o componente só lê `className`.

```html
<!-- CORRETO -->
<ui-text htmlTag="h1" type="body-large-highlight" className="text-primary">Título</ui-text>
<ui-text htmlTag="span" type="body-highlight" className="text-primary">Destaque</ui-text>
<ui-text htmlTag="p" type="body" className="text-secondary">Corpo de texto</ui-text>
<ui-text htmlTag="span" type="small" className="text-neutral">Texto pequeno</ui-text>

<!-- ERRADO — não renderiza os estilos corretamente -->
<ui-text class="text-xl font-bold text-primary">Título</ui-text>
```

Tipos disponíveis (`type`): `"medium"`, `"body-large-highlight"`, `"body-large"`, `"body-highlight"`, `"body"`, `"body-small"`, `"small"`, `"label"`, `"link"`.

Tags comuns (`htmlTag`): `"h1"`, `"h2"`, `"h3"`, `"span"`, `"p"`.

### `ui-info-alert` — uso correto

O `<ui-info-alert>` renderiza blocos de aviso/alerta com ícone, border, background e tipografia automaticamente. **Nunca criar divs custom para alertas** — sempre usar este componente.

```html
<!-- CORRETO — usar ui-info-alert -->
<ui-info-alert type="warning" icon="warning" title="Cuidado" description="Mensagem de aviso." [isVisible]="true"></ui-info-alert>
<ui-info-alert type="error" icon="error" title="Erro" description="Algo deu errado." [isVisible]="true"></ui-info-alert>
<ui-info-alert type="success" icon="success" title="Sucesso" description="Operação concluída." [isVisible]="true"></ui-info-alert>
<ui-info-alert type="info" icon="info" title="Informação" description="Saiba mais." [isVisible]="true"></ui-info-alert>
<ui-info-alert type="primary" icon="primary" title="Dica" description="Sugestão útil." [isVisible]="true"></ui-info-alert>

<!-- ERRADO — div custom para alertas -->
<div class="p-4 bg-surface-warning rounded-2xl border border-warning flex gap-2">
    <ps-icon [icon]="'icon-warning'" class="text-xl text-warning"></ps-icon>
    <ui-text>Texto de aviso</ui-text>
</div>
```

Atributos disponíveis:

| Atributo      | Valores                                                | Notas                                    |
| ------------- | ------------------------------------------------------ | ---------------------------------------- |
| `type`        | `"info"` `"warning"` `"error"` `"success"` `"primary"` | Tipo visual do alerta                    |
| `icon`        | `"info"` `"warning"` `"error"` `"success"` `"primary"` | Ícone automático por tipo                |
| `title`       | string                                                 | Título em bold                           |
| `description` | string                                                 | Texto descritivo                         |
| `[isVisible]` | boolean                                                | Controla visibilidade                    |
| `content`     | `"default"` `"list"` `"details"` `"dimiss"`            | Layout do conteúdo                       |
| `[listItems]` | string[]                                               | Lista de itens (quando `content="list"`) |
| `linkText`    | string                                                 | Texto do link opcional                   |

### Quando criar componente local

- Componente é **específico** de uma feature e não faz sentido compartilhar
- O design system não cobre o caso de uso e criar um novo componente compartilhado não é viável no momento

### Quando criar componente no ui-components

- Componente será usado em **2+ projetos** (zoppy-FE, partners-fe, etc.)
- Componente é genérico o suficiente para ser reutilizado
- Ao criar, adicionar **Storybook story** para documentação

---

## Routing

### Lazy loading obrigatório

Todas as rotas de feature devem usar lazy loading.

```typescript
export const routes: Routes = [
    {
        path: 'customers',
        loadComponent: () => import('./customers/customers.component').then(m => m.CustomersComponent),
        canActivate: [DashboardGuard, FeatureGuard],
        data: { feature: Features.CUSTOMERS, roles: [RoleEnum.MASTER, RoleEnum.ADMIN] }
    }
];
```

### Guards

Usar os guards existentes conforme necessidade:

- `DashboardGuard` — verifica sessão (company/user)
- `FeatureGuard` — valida feature flag via `data.feature`
- `RoleGuard` — controle de acesso via `data.roles`
- `PremiumGuard` / `StandardGuard` — restrição por plano
- `PreventRedirectGuard` — previne navegação com alterações não salvas

---

## Testes Unitários

### Padrão de teste com TestBed

```typescript
describe('FeatureComponent', () => {
    let component: FeatureComponent;
    let fixture: ComponentFixture<FeatureComponent>;
    let featureService: jasmine.SpyObj<FeatureService>;

    beforeEach(waitForAsync(async () => {
        featureService = jasmine.createSpyObj('FeatureService', ['loadItems'], {
            items: signal<Item[]>([]),
            loading: signal(false)
        });

        await TestBed.configureTestingModule({
            imports: [FeatureComponent],
            providers: [{ provide: FeatureService, useValue: featureService }, provideHttpClient(), provideHttpClientTesting()]
        }).compileComponents();

        fixture = TestBed.createComponent(FeatureComponent);
        component = fixture.componentInstance;
    }));

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display items when loaded', () => {
        featureService.items = signal([{ id: '1', name: 'Test' }]);
        fixture.detectChanges();

        const items = fixture.nativeElement.querySelectorAll('[data-testid="item-card"]');
        expect(items.length).toBe(1);
    });

    it('should show skeleton while loading', () => {
        featureService.loading = signal(true);
        fixture.detectChanges();

        const skeleton = fixture.nativeElement.querySelector('app-skeleton');
        expect(skeleton).toBeTruthy();
    });
});
```

### O que testar

- **Componentes**: renderização condicional, inputs/outputs, interações do usuário
- **Services**: chamadas HTTP (com `HttpClientTestingModule`), transformação de dados, estado
- **Pipes**: transformação de valores, edge cases (null, undefined, empty)
- **Guards**: redirecionamento correto, verificação de permissões

### Convenções

- Um `describe` por componente/service
- Um `it` por comportamento
- Usar `data-testid` para seletores em testes (não depender de classes CSS ou estrutura DOM)
- Mock de services com `jasmine.createSpyObj`
- Signals em mocks: usar `signal()` para simular o estado

---

## Convenções gerais

### Estrutura de pastas por feature

```
src/core/pages/dashboard/
└── feature-name/
    ├── feature-name.component.ts
    ├── feature-name.component.html
    ├── feature-name.component.spec.ts
    ├── feature-name.service.ts
    └── components/
        ├── sub-component/
        │   ├── sub-component.component.ts
        │   ├── sub-component.component.html
        │   └── sub-component.component.spec.ts
        └── another-component/
```

### Nomeação

- **Componentes**: `kebab-case` para selector, `PascalCase` para classe
- **Services**: `feature-name.service.ts` → `FeatureNameService`
- **Pipes**: `pipe-name.pipe.ts` → `PipeNamePipe`
- **Guards**: `guard-name.guard.ts` → função `guardNameGuard`
- **Models**: classes em `shared/models/entities/`, requests em `shared/models/requests/`, responses em `shared/models/responses/`

### Não fazer

- Não usar `any` — tipar tudo
- Não omitir o tipo explícito em declarações de signals, inputs e outputs — sempre declarar `const x: WritableSignal<T> = signal(value)`
- Não usar `console.log` em código commitado
- Não fazer subscribe sem cleanup (usar `takeUntilDestroyed()` ou `toSignal()`)
- Não criar componentes com 500+ linhas — extrair sub-componentes
- Não fazer lógica de negócio no template — mover para `computed()` ou métodos
- Não importar módulos inteiros quando só precisa de um componente standalone
- Não hardcodar strings de UI — usar constantes ou i18n
- Não adicionar padding no container raiz de componentes de modal — o `ModalService` já adiciona padding via `modal-content`
