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
    templateUrl: './feature.component.html',
})
export class FeatureComponent {}
```

### Signals como padrão

Usar Angular Signals para estado de componente. Evitar `@Input()` / `@Output()` decorators — usar a API funcional.

```typescript
// CORRETO — Signals API
export class FeatureComponent {
    // Inputs
    title = input.required<string>();
    description = input<string>('');

    // Outputs
    saved = output<void>();
    deleted = output<string>();

    // Estado local
    loading = signal(false);
    items = signal<Item[]>([]);

    // Estado derivado
    hasItems = computed(() => this.items().length > 0);
    filteredItems = computed(() => this.items().filter(i => !i.archived));
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
} @else {
    @for (item of items(); track item.id) {
        <app-item-card [item]="item" />
    }
}

@switch (status()) {
    @case ('active') { <ui-tag-pill variant="success">Ativo</ui-tag-pill> }
    @case ('inactive') { <ui-tag-pill variant="warning">Inativo</ui-tag-pill> }
}
```

```html
<!-- EVITAR -->
<app-skeleton *ngIf="loading"></app-skeleton>
<app-item-card *ngFor="let item of items" [item]="item"></app-item-card>
```

### Smart vs Dumb Components

- **Smart (container)**: injetam services, coordenam dados, possuem lógica. São as pages e features.
- **Dumb (presentational)**: recebem dados via `input()`, emitem eventos via `output()`, zero lógica de negócio.

```
pages/
└── customers/
    ├── customers.component.ts          # Smart — injeta service, carrega dados
    └── components/
        ├── customer-card.component.ts   # Dumb — recebe Customer via input
        └── customer-filters.component.ts # Dumb — emite filtros via output
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
            @case ('currency') { <ui-text>{{ value() | zoppyCurrency }}</ui-text> }
            @case ('percentage') { <ui-text>{{ value() | zoppyPercent }}</ui-text> }
            @case ('number') { <ui-text>{{ value() | zoppyRound }}</ui-text> }
            @case ('date') { <ui-text>{{ value() | zoppyDateMask: 'DD/MM/YYYY' }}</ui-text> }
            @default { <ui-text>{{ value() }}</ui-text> }
        }
    `,
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

### Singleton com `providedIn: 'root'`

Todos os services devem ser singleton injetados no root. Não declarar em `providers` de componentes.

```typescript
@Injectable({ providedIn: 'root' })
export class CustomerService extends ApiService {
    // ...
}
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
                next: (response) => this.items.set(response),
                error: (error) => this.toast.error(error.message),
            });
    }
}
```

### Estado reativo entre componentes

Para estado compartilhado entre componentes que não têm relação pai-filho, usar services com signals. Evitar `BehaviorSubject` em código novo — preferir signals.

```typescript
// CORRETO — Signal-based
@Injectable({ providedIn: 'root' })
export class SidebarService {
    expanded = signal(false);
    toggle() { this.expanded.update(v => !v); }
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
        data: { feature: Features.CUSTOMERS, roles: [RoleEnum.MASTER, RoleEnum.ADMIN] },
    },
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
            loading: signal(false),
        });

        await TestBed.configureTestingModule({
            imports: [FeatureComponent],
            providers: [
                { provide: FeatureService, useValue: featureService },
                provideHttpClient(),
                provideHttpClientTesting(),
            ],
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
- Não usar `console.log` em código commitado
- Não fazer subscribe sem cleanup (usar `takeUntilDestroyed()` ou `toSignal()`)
- Não criar componentes com 500+ linhas — extrair sub-componentes
- Não fazer lógica de negócio no template — mover para `computed()` ou métodos
- Não importar módulos inteiros quando só precisa de um componente standalone
- Não hardcodar strings de UI — usar constantes ou i18n
