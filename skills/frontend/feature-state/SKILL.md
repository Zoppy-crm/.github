---
name: feature-state
description: How to manage state and avoid prop drilling in the Zoppy FE project. Use whenever shared state is needed between components, when data would need to be passed through more than one input() level, or when creating a state service for a feature. Triggers on phrases like "share state between components", "avoid prop drilling", "manage feature state", "create a state service".
---

# Zoppy Feature State Management

## The Core Rule

**Never pass data through more than one `input()` level.** If a grandchild component needs data, inject a service — do not thread it through the parent.

```
// BAD — prop drilling
DashboardPage
  → [user]="user" → FeatureContainer
      → [user]="user" → SubComponent
          → [user]="user" → DeepComponent   ← user drilled 3 levels
```

```
// GOOD — service injection
DashboardPage
FeatureContainer
SubComponent
DeepComponent  ← all inject UserService directly
```

---

## Choosing the Right Scope

| Situation | Solution |
|-----------|----------|
| State used across the entire app (user, company, sidebar) | `providedIn: 'root'` |
| State shared between sibling components within a feature | `providedIn: 'root'` state service scoped by feature |
| State that must reset when the feature component is destroyed | Service provided in the container's `providers` array |

---

## Global State Service (`providedIn: 'root'`)

Use when the state must persist across navigation or is consumed by unrelated components.

```typescript
// src/shared/services/sidebar/sidebar.service.ts
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SidebarService {
    readonly expanded = signal(false);

    toggle(): void {
        this.expanded.update(v => !v);
    }
}
```

Any component simply injects it — no prop drilling:

```typescript
export class TopBarComponent {
    private readonly sidebar = inject(SidebarService);
    protected readonly isExpanded = this.sidebar.expanded;
}
```

---

## Feature State Service (scoped to a container)

Use when the state belongs exclusively to one feature and must be cleaned up when the user leaves.

Provide the service in the container's `providers` array. This creates a **new instance** for that subtree and destroys it when the container is destroyed.

```typescript
// create-product/create-product.state.service.ts
import { Injectable, signal, computed } from '@angular/core';
import { ProductRequest } from 'src/shared/models/requests/product/product.request';

@Injectable()   // <-- no providedIn
export class CreateProductStateService {
    readonly name = signal('');
    readonly price = signal<number | null>(null);
    readonly categoryId = signal<string | null>(null);
    readonly loading = signal(false);
    readonly error = signal<string | null>(null);

    readonly isValid = computed(() =>
        this.name().trim().length > 0 && this.price() !== null && this.categoryId() !== null
    );

    readonly formValue = computed<ProductRequest>(() => ({
        name: this.name(),
        price: this.price()!,
        categoryId: this.categoryId()!,
    }));

    reset(): void {
        this.name.set('');
        this.price.set(null);
        this.categoryId.set(null);
        this.error.set(null);
    }
}
```

Provide it in the smart container:

```typescript
// create-product.component.ts
@Component({
    selector: 'app-create-product',
    standalone: true,
    providers: [CreateProductStateService],   // <-- scoped instance
    imports: [ProductFormComponent, ProductSummaryComponent],
    templateUrl: './create-product.component.html',
})
export class CreateProductComponent {
    readonly state = inject(CreateProductStateService);
}
```

Sub-components inject the same scoped instance — no props needed:

```typescript
// components/product-form/product-form.component.ts
export class ProductFormComponent {
    private readonly state = inject(CreateProductStateService);
    // reads state.name(), state.price(), etc. directly
}
```

---

## Signal Patterns

### Reading state

```typescript
// In template — always call as function
{{ state.name() }}
@if (state.loading()) { <ui-spinner /> }

// In computed
readonly label = computed(() => `Product: ${this.state.name()}`);
```

### Updating state

```typescript
// set — replace value
this.state.name.set('New Name');

// update — derive from previous value
this.state.items.update(items => [...items, newItem]);

// Updating a field inside an object array (immutable)
this.state.items.update(items => {
    const updated = [...items];
    updated[index] = { ...updated[index], name: 'Updated' };
    return updated;
});
```

### Derived state with `computed()`

```typescript
readonly totalPrice = computed(() =>
    this.state.items().reduce((sum, item) => sum + item.price, 0)
);

readonly hasItems = computed(() => this.state.items().length > 0);
```

---

## Before / After: Prop Drilling → State Service

### Before (prop drilling)

```typescript
// ❌ container passes everything down
@Component({ template: `
    <app-step-one [product]="product" [loading]="loading" (productChange)="product = $event" />
    <app-step-two [product]="product" [categories]="categories" (categoryChange)="product.categoryId = $event" />
    <app-step-three [product]="product" [loading]="loading" (save)="save()" />
` })
export class CreateProductComponent {
    product: Partial<ProductRequest> = {};
    categories: CategoryEntity[] = [];
    loading = false;
}
```

### After (state service)

```typescript
// ✅ container is thin; sub-components inject state directly
@Component({ template: `
    <app-step-one />
    <app-step-two />
    <app-step-three (save)="save()" />
`, providers: [CreateProductStateService] })
export class CreateProductComponent {
    private readonly state = inject(CreateProductStateService);
    async save() { /* uses state.formValue() directly */ }
}

// Each step reads/writes state independently
export class StepOneComponent {
    private readonly state = inject(CreateProductStateService);
    protected readonly name = this.state.name;
    updateName(value: string) { this.state.name.set(value); }
}
```

---

## Cleanup

Scoped services (provided in container) are automatically destroyed. Global services should expose a `reset()` method called by the container on destroy when the state is feature-specific:

```typescript
export class CreateProductComponent implements OnDestroy {
    private readonly state = inject(CreateProductStateService);

    ngOnDestroy(): void {
        this.state.reset();
    }
}
```

---

## What NOT to do

```typescript
// BAD — BehaviorSubject in new code
@Injectable({ providedIn: 'root' })
export class FeatureService {
    private _items = new BehaviorSubject<Item[]>([]);
    items$ = this._items.asObservable();
}

// GOOD — WritableSignal
@Injectable({ providedIn: 'root' })
export class FeatureService {
    readonly items = signal<Item[]>([]);
}
```

```typescript
// BAD — component holds all state and passes it down
export class PageComponent {
    items: Item[] = [];
    selected: Item | null = null;
    loading = false;
    // passes all three to every child via @Input
}

// GOOD — state service holds it; children inject it
@Injectable()
export class PageStateService {
    readonly items = signal<Item[]>([]);
    readonly selected = signal<Item | null>(null);
    readonly loading = signal(false);
}
```
