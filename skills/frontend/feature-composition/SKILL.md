---
name: feature-composition
description: How to create a new feature in the Zoppy FE project following the composition pattern. Use whenever the user wants to create a new dashboard page, feature section, modal flow, or sub-feature. Triggers on phrases like "create a feature", "add a page", "build a new section", "create a form for X".
---

# Zoppy Feature Composition

Every new feature must be **self-contained**: one folder holds everything the feature needs — component, sub-components, state service, and routes. Nothing leaks into other folders unless it is genuinely shared across 2+ features.

## Folder Structure

New features live under `src/core/pages/dashboard/<feature-name>/`:

```
src/core/pages/dashboard/
└── create-product/                          # feature root
    ├── create-product.component.ts          # smart container
    ├── create-product.component.html
    ├── create-product.component.spec.ts
    ├── create-product.state.service.ts      # feature state (if needed)
    ├── create-product.routes.ts             # child routes (if multi-step)
    └── components/                          # sub-components (focused, single-responsibility)
        ├── product-form/
        │   ├── product-form.component.ts
        │   ├── product-form.component.html
        │   └── product-form.component.spec.ts
        ├── product-image-upload/
        │   ├── product-image-upload.component.ts
        │   └── product-image-upload.component.html
        └── product-summary/
            ├── product-summary.component.ts
            └── product-summary.component.html
```

## Container vs Sub-Components

**Smart container** (`create-product.component.ts`):

- Injects data services (HTTP, repositories)
- Manages data loading and saving
- Handles navigation
- Provides the feature state service via `providers: [FeatureStateService]`
- Does NOT contain visual/presentation logic — delegates to sub-components

**Sub-components** (inside `components/`):

- Focused on a single responsibility (form, summary, upload…)
- **May and should** inject services directly — state services, API services, or any other shared service
- Use `input()` / `output()` only when the value comes from **outside the feature scope**

## Component Size Rule

A component file must not exceed **~150 lines**. When it grows beyond that, extract a sub-component.

## Smart Container Example

```typescript
// create-product.component.ts
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { ProductService } from 'src/shared/services/product/product.service';
import { CreateProductStateService } from './create-product.state.service';
import { ProductFormComponent } from './components/product-form/product-form.component';
import { ProductSummaryComponent } from './components/product-summary/product-summary.component';

@Component({
    selector: 'app-create-product',
    standalone: true,
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [ProductFormComponent, ProductSummaryComponent],
    templateUrl: './create-product.component.html'
})
export class CreateProductComponent {
    private readonly router = inject(Router);
    private readonly productService = inject(ProductService);
    readonly state = inject(CreateProductStateService);

    async save(): Promise<void> {
        if (this.state.loading()) return;
        this.state.loading.set(true);
        try {
            await this.productService.create(this.state.formValue());
            this.router.navigate(['/dashboard/products']);
        } finally {
            this.state.loading.set(false);
        }
    }
}
```

```html
<!-- create-product.component.html -->
<!-- Sub-componentes injetam o state service diretamente — sem passar props -->
<div class="flex flex-col gap-6 p-6">
    <app-product-form />
    <app-product-summary />
    <div class="flex justify-end gap-3">
        <ui-button variant="secondary" (clicked)="router.navigate(['/dashboard/products'])">Cancel</ui-button>
        <ui-button [loading]="state.loading()" (clicked)="save()">Save</ui-button>
    </div>
</div>
```

## Sub-Component Example (injetando state service)

```typescript
// components/product-form/product-form.component.ts
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { UiInputComponent } from '@Zoppy-crm/ui-input';
import { CreateProductStateService } from '../../create-product.state.service';

@Component({
    selector: 'app-product-form',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [UiInputComponent],
    templateUrl: './product-form.component.html'
})
export class ProductFormComponent {
    // Injeta o state service diretamente — sem prop drilling
    protected readonly state = inject(CreateProductStateService);
}
```

```html
<!-- product-form.component.html -->
<ui-input [value]="state.name()" (valueChange)="state.name.set($event)" />
<ui-input type="number" [value]="state.price()" (valueChange)="state.price.set($event)" />
```

> Use `input()` / `output()` apenas quando o dado vem **de fora do escopo da feature** (ex: um componente reutilizável que não conhece o state service).

## Adding the Route

Register with lazy loading in `dashboard.routes.ts`:

```typescript
// src/core/pages/dashboard/dashboard.routes.ts
{
    path: 'products/create',
    loadComponent: () =>
        import('./create-product/create-product.component').then(m => m.CreateProductComponent),
    canActivate: [FeatureGuard],
    data: { feature: Features.CrmProduct },
},
```

For multi-step features with child routes, create a dedicated `create-product.routes.ts` and use `loadChildren`:

```typescript
{
    path: 'products/create',
    loadChildren: () =>
        import('./create-product/create-product.routes').then(m => m.createProductRoutes),
    canActivate: [FeatureGuard],
    data: { feature: Features.CrmProduct },
},
```

## Composition Hierarchy

```
CreateProductComponent (container — injeta serviços HTTP, faz save/navigation)
│  providers: [CreateProductStateService]
├── ProductFormComponent (sub-component — injeta CreateProductStateService)
│   ├── ProductImageUploadComponent (sub-component — injeta CreateProductStateService)
│   └── CategorySelectorComponent (sub-component — injeta CreateProductStateService)
└── ProductSummaryComponent (sub-component — injeta CreateProductStateService)
```

## Checklist

- [ ] Feature folder created under `src/core/pages/dashboard/<feature-name>/`
- [ ] Smart container injeta serviços HTTP e provê o `FeatureStateService` via `providers: [...]`
- [ ] Sub-components injetam o `FeatureStateService` diretamente — sem prop drilling
- [ ] No component exceeds ~150 lines
- [ ] Sub-components are in `components/<sub-name>/` sub-folders
- [ ] Route registered with `loadComponent` (lazy loading)
- [ ] Feature state extracted to `<feature-name>.state.service.ts` if state is shared between sub-components
- [ ] Styling done exclusively with Tailwind — no inline SCSS unless strictly necessary
- [ ] `ChangeDetectionStrategy.OnPush` on all components
- [ ] `@Zoppy-crm/*` design system components used instead of custom HTML when available

## What NOT to do

```typescript
// BAD — one god component doing everything
export class CreateProductComponent {
    // 300 lines of form logic, validation, HTTP calls, sub-feature rendering
    name = '';
    price = 0;
    category = '';
    imageUrl = '';
    // ... 20 more fields
    validateForm() { ... }
    renderImagePreview() { ... }
    fetchCategories() { ... }
    save() { ... }
}
```

```typescript
// GOOD — container delegates to focused sub-components
export class CreateProductComponent {
    readonly state = inject(CreateProductStateService);
    save() { ... }  // ~10 lines
}
```
