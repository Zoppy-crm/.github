---
name: flow-template-guard
description: Valida se um plano de fase tem templates de referência e/ou design de referência, e decide a estratégia de implementação — cópia literal ou processamento. Deve ser chamada ANTES de implementar qualquer fase no beta-dev-guide. Use sempre que for iniciar a implementação de uma fase de um plano existente.
---

# Template Guard — Validação pré-implementação

Skill complementar ao `beta-dev-guide`. Deve ser executada **antes de cada fase** para decidir a estratégia de implementação: copiar templates literalmente ou processar do zero.

## Quando executar

**Sempre** antes de iniciar a implementação de uma fase. O `beta-dev-guide` chama esta skill automaticamente no passo 0.

## Workflow

### 1. Analisar o plano da fase

Ler o plano detalhado da fase (ex: `docs/plans/fase-05-selecao-lojas.md`) e identificar:

-   [ ] Tem seção `## Design de Referência` com imagem?
-   [ ] Tem seção `### Template de Referência` com blocos de código HTML?
-   [ ] Tem seção com blocos de código TypeScript (`.ts`) de componentes?
-   [ ] Tem seção `### Reuso do Design System` com mapeamento de elementos?
-   [ ] Tem seção `### Estilização (Tailwind)` com classes definidas?

### 2. Carregar e verificar a imagem de design (se existir)

Se o plano referencia uma imagem:

1. Ler a imagem com o tool `Read`
2. Comparar visualmente a imagem com os templates HTML do plano
3. Identificar se os templates correspondem ao design

### 3. Decidir a estratégia

```
┌─────────────────────────────────────────────────┐
│ O plano tem templates HTML com estilos definidos │
│ (classes Tailwind, atributos de componentes,     │
│  className, type, icon, etc.)?                   │
└────────────────────┬────────────────────────────┘
                     │
              ┌──────┴──────┐
              │ SIM         │ NÃO
              ▼             ▼
    MODO: CÓPIA LITERAL    MODO: PROCESSAMENTO
```

**MODO CÓPIA LITERAL** (preferido):

> Os templates do plano já definem estilos, atributos e estrutura. A implementação deve copiar **cada linha exatamente como está**, fazendo apenas:
>
> -   Ajustes de compilação (tipos TypeScript, imports)
> -   Correção de tokens Figma PascalCase → Tailwind kebab-case (conforme tabela da skill `design-to-plan`)
> -   Adaptações de API de componentes do DS (ex: `(clicked)` → `(onClick)`, `<switch>` → `<ui-switch>`)
> -   Migração de componentes descontinuados `ps-*` → `ui-*` (ex: `<ps-icon>` → `<ui-icon>`, `<ps-button>` → `<ui-button>` — drop-in, mesma assinatura)
>
> **NÃO FAZER neste modo:**
>
> -   Remover atributos que "parecem desnecessários" (ex: `className="text-primary"`)
> -   Simplificar estrutura HTML
> -   Trocar nomes de ícones
> -   Alterar tamanhos/tipos de componentes
> -   Omitir propriedades de componentes do DS

**MODO PROCESSAMENTO** (quando o plano não tem templates):

> O plano tem apenas descrição textual ou hierarquia de componentes sem templates HTML. Neste caso:
>
> 1. Usar a imagem de design como referência visual
> 2. Consultar a skill `design-to-plan` para mapeamento de componentes
> 3. Construir os templates seguindo as convenções do projeto

### 4. Reportar a decisão

Antes de implementar, comunicar ao dev:

**Se CÓPIA LITERAL:**

```
📋 Fase [N] — Template Guard
   Estratégia: CÓPIA LITERAL
   Templates encontrados: [X] blocos HTML, [Y] blocos TypeScript
   Design de referência: [sim/não]
   Tokens PascalCase para corrigir: [lista ou "nenhum"]
   Pronto para implementar.
```

**Se PROCESSAMENTO:**

```
📋 Fase [N] — Template Guard
   Estratégia: PROCESSAMENTO (plano sem templates definidos)
   Design de referência: [sim/não]
   Componentes do DS a usar: [lista]
   Pronto para implementar.
```

### 5. Checklist pós-implementação (CÓPIA LITERAL)

Após implementar cada componente, percorrer este checklist **antes de declarar o passo concluído**:

Para cada `<ui-text>` no template do plano:

-   [ ] `htmlTag` presente e idêntico ao plano?
-   [ ] `type` presente e idêntico ao plano?
-   [ ] `className` presente e idêntico ao plano? (NÃO omitir)

Para cada `<ui-button>` no template do plano:

-   [ ] `type` presente e idêntico ao plano?
-   [ ] `size` presente e idêntico ao plano?
-   [ ] `text` presente e idêntico ao plano?
-   [ ] `icon` e `[iconBefore]`/`[iconAfter]` presentes se o plano define?
-   [ ] `[wide]` presente se o plano define?

Para cada `<ui-icon>` no template do plano (se o plano trouxer `<ps-icon>`, implementar como `<ui-icon>` — mesma assinatura):

-   [ ] `[icon]` presente e idêntico ao plano?
-   [ ] `class` presente e idêntico ao plano?

Para cada div/container no template do plano:

-   [ ] Classes Tailwind presentes e idênticas? (exceto PascalCase → kebab-case)

**Se algum atributo do plano foi omitido no código, corrigir ANTES de avançar.**

---

## Regras

-   **Esta skill é obrigatória antes de cada fase** — não pular
-   **CÓPIA LITERAL é sempre a estratégia preferida** quando o plano tem templates
-   **Nunca "melhorar" ou "simplificar" um template do plano** — se algo parece errado, reportar ao dev em vez de corrigir silenciosamente
-   **O checklist pós-implementação é obrigatório no modo CÓPIA LITERAL** — percorrer cada componente do DS
-   **Se o plano tem tokens PascalCase**, listar todos ANTES de implementar para que a correção seja consciente, não acidental
