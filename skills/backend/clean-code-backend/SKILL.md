---
name: clean-code-backend
description: Padrões de clean code para application services no zoppy-api. Cobre separação de responsabilidades, extração de métodos, nomenclatura, limites de complexidade e patterns de agregação. Use ao escrever, revisar ou refatorar application services.
---

# Clean Code — Application Services (zoppy-api)

Regras para escrever application services legíveis, testáveis e manuteníveis.

---

## Estrutura de um método público

Todo método público segue a mesma sequência:

```
1. Validar entrada (early returns / throw exceptions)
2. Buscar dados (queries ao domain)
3. Processar (lógica de negócio — delegar para privados se complexo)
4. Retornar (construir response DTO)
```

```typescript
// BOM — cada seção clara, ~20 linhas
public async getMetrics(type: string, id: string): Promise<IntegrationMetricsResponse> {
    this.validateType(type);

    const orderSyncs: DataSyncManagement[] = await this.findOrderSyncs(type, id);

    const metrics: AggregatedMetrics = this.calculateMetrics(orderSyncs);

    return this.buildMetricsResponse(metrics, orderSyncs);
}

// RUIM — tudo no mesmo método, 50+ linhas
public async getMetrics(type: string, id: string): Promise<IntegrationMetricsResponse> {
    if (type !== 'erp' && type !== 'ecommerce') throw new BadRequestException('...');
    const companyId = this.session.getCompany().id;
    const whereClause = { entity: DataSyncEntity.Orders, companyId };
    if (type === 'erp') whereClause.erpKeyId = id;
    else whereClause.keyId = id;
    const syncs = await this.dataSyncManagementDomain.find({ where: whereClause });
    const totalProcessed = syncs.reduce((sum, s) => sum + s.processedRecords, 0);
    // ... mais 20 linhas de cálculo e construção de response
}
```

---

## Limites de complexidade

| Métrica | Limite | Ação quando excede |
|---------|--------|--------------------|
| **Linhas por método público** | ~20-25 | Extrair para métodos privados |
| **Linhas por método privado** | ~15-20 | Extrair para helper ou subdividir |
| **Nesting depth** | 2 níveis | Usar early returns ou extrair |
| **Parâmetros** | 4 max | Usar options object / interface |
| **Responsabilidades** | 1 por método | Separar validação, query, cálculo, response |

---

## Extração de métodos privados

### Quando extrair

- Bloco de código tem um **propósito nomeável** ("calcular métricas", "construir response")
- Método público excede ~25 linhas
- Lógica de `reduce`, `map`, `filter` com mais de 1 transformação
- Condicional complexa (if/else com lógica de negócio nos dois branches)

### Nomenclatura de métodos privados

| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `validate` | Validação com throw | `validateType(type)` |
| `find` / `fetch` | Query ao domain | `findOrderSyncs(type, id)` |
| `calculate` / `compute` | Lógica de cálculo puro | `calculateMetrics(syncs)` |
| `build` / `map` | Construção de DTO/response | `buildMetricsResponse(metrics)` |
| `create` / `save` | Persistência | `createIntegration(request)` |
| `queue` / `dispatch` | Enfileiramento | `queueProcessing(data)` |

### Posição no arquivo

Métodos privados ficam **após** os métodos públicos, agrupados por responsabilidade:

```typescript
@Injectable()
export class MyApplication {
    constructor(...) {}

    // --- Métodos públicos ---
    public async create(request: Request): Promise<Response> { ... }
    public async findById(id: string): Promise<Response> { ... }

    // --- Validação ---
    private validateType(type: string): void { ... }
    private validateRequest(request: Request): void { ... }

    // --- Queries ---
    private async findOrderSyncs(type: string, id: string): Promise<DataSyncManagement[]> { ... }

    // --- Cálculos ---
    private calculateMetrics(syncs: DataSyncManagement[]): AggregatedMetrics { ... }

    // --- Response builders ---
    private buildMetricsResponse(metrics: AggregatedMetrics, syncs: DataSyncManagement[]): Response { ... }
}
```

---

## Interfaces para dados intermediários

Quando um cálculo produz múltiplos valores, criar uma interface para o resultado intermediário — não retornar tuplas ou objetos anônimos.

```typescript
// BOM — interface clara
interface AggregatedMetrics {
    totalProcessed: number;
    totalRecords: number;
    successRate: number;
    errorRate: number;
}

private calculateMetrics(syncs: DataSyncManagement[]): AggregatedMetrics {
    const totalProcessed: number = syncs.reduce(
        (sum: number, sync: DataSyncManagement) => sum + (sync.processedRecords ?? 0), 0
    );
    // ...
    return { totalProcessed, totalRecords, successRate, errorRate };
}

// RUIM — objeto anônimo
private calculateMetrics(syncs: any[]): { a: number; b: number; c: number } { ... }
```

---

## Tipagem explícita

Nunca usar `any` em variáveis intermediárias. Sempre tipar:

```typescript
// BOM
const orderSyncs: DataSyncManagement[] = await this.findOrderSyncs(type, id);
const totalProcessed: number = orderSyncs.reduce(...);

// RUIM
const syncs: any[] = await this.domain.find({ where: whereClause });
const total = syncs.reduce((sum, s) => sum + s.processedRecords, 0);
```

---

## Early returns para validação

```typescript
// BOM — flat, claro
private validateType(type: string): void {
    const validTypes: string[] = ['erp', 'ecommerce'];
    if (!validTypes.includes(type)) {
        throw new BadRequestException(`Tipo inválido "${type}". Use: ${validTypes.join(', ')}`);
    }
}

// RUIM — nesting desnecessário
if (type === 'erp' || type === 'ecommerce') {
    // 40 linhas de lógica
} else {
    throw new BadRequestException('...');
}
```

---

## Cálculos com segurança

Proteger contra divisão por zero e arredondar resultados:

```typescript
private calculateRate(numerator: number, denominator: number): number {
    if (denominator === 0) return 0;
    return Math.round((numerator / denominator) * 10000) / 100; // 2 casas decimais
}
```

---

## Response builders

Separar a construção do DTO de response da lógica de negócio:

```typescript
// BOM — builder isolado
private buildMetricsResponse(
    metrics: AggregatedMetrics,
    orderSyncs: DataSyncManagement[],
): IntegrationMetricsResponse {
    return {
        processedOrders: metrics.totalProcessed,
        successRate: metrics.successRate,
        errorRate: metrics.errorRate,
        lastSyncAt: orderSyncs[0]?.updatedAt ?? null,
        oldestOrderAt: null,
        createdAt: orderSyncs[orderSyncs.length - 1]?.createdAt ?? new Date(),
    };
}
```

---

## Checklist antes de finalizar um application service

- [ ] Nenhum método público excede ~25 linhas
- [ ] Cada método tem uma única responsabilidade
- [ ] Nesting máximo de 2 níveis
- [ ] Nenhum `any` em variáveis — tudo tipado
- [ ] Variáveis com nomes completos e descritivos (nunca `i`, `s`, `k`)
- [ ] Validações no início com early returns
- [ ] Cálculos complexos extraídos para métodos privados
- [ ] Interfaces para dados intermediários (não objetos anônimos)
- [ ] Response construído em método separado (quando > 5 campos)
- [ ] `companyId` vem de `this.session.getCompany().id`
