---
name: zoppy-design-system-figma
description: >
  Skill de verificação do Design System Zoppy antes de qualquer execução no Figma. Etapa obrigatória entre Ideação e Prototipação. Verifica se já existe padrão no DS para a solução escolhida, mapeia componentes disponíveis e aprovados, identifica componentes em desenvolvimento (proibidos), define tokens de cor, tipografia e espaçamento a usar, e entrega a lista de referências do DS prontas para uso na prototipação. Nunca criar componente novo sem antes confirmar que não existe equivalente.

  Acionar quando: direção de ideação foi escolhida e é hora de mapear o que o DS oferece antes de ir para o Figma. Também acionar quando houver dúvida sobre "qual componente usar aqui", "esse padrão já existe no DS?", "posso usar esse componente?", "quais tokens usar nessa tela?".
---

# Skill: Design System & Figma Check — Zoppy

Você verifica o Design System da Zoppy antes de qualquer execução no Figma. Seu trabalho é garantir que a prototipação vai usar apenas componentes e tokens aprovados — e nunca criar do zero o que já existe.

Você opera sob um princípio absoluto:
**Nunca criar componente novo sem confirmar que não existe equivalente no DS.** Criar fora do DS fragmenta a consistência do produto e gera retrabalho no dev.

---

## Posição no fluxo

```
Discovery → Briefing → Ideação → DS Check ← VOCÊ ESTÁ AQUI → Prototipação → Handoff
```

**Entrada:** direção de ideação escolhida pela designer (output de `zoppy-ideation-designer`)
**Saída:** lista de componentes aprovados, tokens mapeados, componentes proibidos identificados, referências de arquivo para uso na prototipação

---

## Referências fixas do DS Zoppy

### File key do Design System
```
DS Principal: iCUju2TRogzUxwUaa9v8dt
```

### Component Keys — DS Zoppy (Design System 2024)

| Componente | Key | Status |
|---|---|---|
| Button | `c53e10335aa9a5747facd0ed1725c8ad3afb199e` | ✅ Aprovado |
| Alert | `56836a7296c19104d9a7bffd30c2b7195b367080` | ✅ Aprovado |
| Topbar | `af5bc75e6e23734a037bdd6cd6c414bce88b8347` | ✅ Aprovado |
| Menu options | `036b1b5eb38ff2c3bf90920cf50f0e9b3ab1157c` | ✅ Aprovado |
| Pill / Tag | `95c88bd34d977849a87999075836a6a0ef004c7a` | ✅ Aprovado |
| Label | `95c88bd34d977849a87999075836a6a0ef004c7a` | ✅ Aprovado |
| Radio Button | `b9da93cfd5ec244f53f0766b370e9b8a05b46933` | ✅ Aprovado |
| Icon Button | `7ceb30c7d23585fbfdfa71b4e7ed434f325db4d5` | ✅ Aprovado |
| Toggle | `84c8e556edecf94892674b2d24fd0a0891611cdb` | ✅ Aprovado |
| Input | — | ⚠️ Verificar versão atual no DS antes de usar |
| Modal | — | ⚠️ Verificar se existe componente ou usar Auto Layout |
| Dropdown | — | ⚠️ Verificar versão atual no DS antes de usar |
| Table | — | ⚠️ Construir via Auto Layout + Row do DS |
| Pagination | — | ⚠️ Verificar disponibilidade antes de usar |

> **Regra:** qualquer componente não listado acima como "Aprovado" deve ser verificado no DS antes de usar na prototipação. Em dúvida: verificar via `Figma:use_figma` antes de prosseguir.

---

## Variáveis de cor — tokens disponíveis

### Superfícies
| Token | Uso |
|---|---|
| `Surface/Default` | Fundo padrão de página e containers neutros |
| `Surface/Primary` | Estado selecionado, ativo, destaque primário |
| `Surface/Secondary` | Seções secundárias, backgrounds de cards |
| `Surface/Invert` | Elementos invertidos (ex: chip escuro) |
| `Surface/Success` | Feedback positivo, estados de sucesso |
| `Surface/Warning` | Estado de atenção, pendência, risco baixo |
| `Surface/Critical` | Estado de erro, bloqueio, risco alto |

### Bordas
| Token | Uso |
|---|---|
| `Border/Default` | Borda neutra padrão |
| `Border/Primary` | Borda de elemento selecionado ou ativo |
| `Border/Success` | Borda de estado positivo |
| `Border/Warning` | Borda de estado de atenção |
| `Border/Critical` | Borda de estado de erro |

### Texto
| Token | Uso |
|---|---|
| `Text/Default` | Texto principal, títulos, labels |
| `Text/Neutral` | Texto secundário, descrições, hints |
| `Text/Primary` | Texto em destaque primário (links, ações) |
| `Text/Success` | Texto em contexto positivo |
| `Text/Warning` | Texto em contexto de atenção |
| `Text/Critical` | Texto em contexto de erro |
| `Text/Invert` | Texto em fundo escuro |

### Ações / Interativos
| Token | Uso |
|---|---|
| `Action/Primary` | CTA principal, botão primário |
| `Action/Secondary` | Botão secundário, ação alternativa |
| `Action/Destructive` | Ação destrutiva (deletar, remover) |

---

## Text styles — hierarquia tipográfica

| Token | Uso |
|---|---|
| `Large` | Título de página |
| `Medium` | Título de seção |
| `Small` | Subtítulo de modal, título de card |
| `Body Highlight` | Label de campo, texto de ênfase no corpo |
| `Body` | Corpo de texto padrão |
| `Body small` | Texto auxiliar, hint, nota |
| `Caption` | Label secundário, metadado, timestamp |
| `Label` | Badge, tag numérica |

**Regra:** nunca definir `fontSize` ou `fontFamily` diretamente. Sempre via `textStyleId` do DS ou via `applyTextStyle(node, tokenName)`.

---

## Espaçamento e grid

**Grid base:** 8px
**Padding de containers:** múltiplos de 8px (8, 16, 24, 32, 40, 48)
**Gap entre elementos:** múltiplos de 4px (4, 8, 12, 16, 24)
**Corner radius:** 8px (cards pequenos), 12px (cards médios), 16px (modais e drawers)

**Hierarquia de espaçamento (Gestalt):** containers externos recebem mais padding que elementos internos. Nunca o contrário.

---

## Protocolo de execução do DS Check

### 1. Mapear a solução em componentes

A partir da variante escolhida na ideação, liste cada elemento da interface e classifique:

| Elemento da interface | Componente DS | Status | Alternativa se indisponível |
|---|---|---|---|
| [ex: botão de CTA principal] | Button — variante Primary | ✅ Aprovado | — |
| [ex: card de status] | Auto Layout + Surface/Warning | ✅ Aprovado | — |
| [ex: dropdown de filtro] | — | ⚠️ Verificar | Input — variante Select |

### 2. Verificar componentes marcados como ⚠️

Para cada componente não confirmado:
- Buscar no DS via `Figma:use_figma` com query no arquivo `iCUju2TRogzUxwUaa9v8dt`
- Se encontrado: adicionar key na tabela e marcar como ✅
- Se não encontrado: registrar como "Construir via Auto Layout" com especificação dos tokens

### 3. Listar componentes proibidos

Componentes que não devem ser usados nesta entrega por estarem em desenvolvimento ou fora do escopo:
- [listar qualquer componente que o PM, eng ou design confirmaram como fora de escopo]
- Qualquer componente não encontrado no DS deve ser construído via primitivos (Auto Layout + tokens de cor e tipografia)

### 4. Entregar lista de componentes aprovados

Lista final, pronta para ser usada pela `zoppy-prototyping-figma`:

```
Componentes do DS a usar:
- [Componente] — key: [key] — variante: [variante]

Tokens de cor a usar:
- Superfície: [tokens]
- Texto: [tokens]
- Borda: [tokens]

Construções via Auto Layout (sem componente DS):
- [Elemento] — especificação: [padding, gap, corner radius, tokens de cor]

Componentes proibidos nesta entrega:
- [Componente] — motivo: [em desenvolvimento / fora de escopo / substituído por X]
```

---

## Bloco de Status da Etapa

```markdown
## Status da Etapa — DS / Figma Check

- **Pode avançar?** [Sim / Não / Condicional]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi decidido:**
  - [componentes confirmados]
  - [tokens mapeados]
  - [estrutura de Auto Layout definida]
- **Hipóteses que ainda precisam ser validadas:**
  - [componentes marcados como ⚠️ que precisam ser verificados no Figma antes de usar]
- **Lacunas abertas:**
  - [elementos da solução sem componente equivalente no DS]
- **Recomendação:** [Avançar / Revisar / Pausar]
- **Motivo:** [1-2 linhas]
```

---

## Anti-padrões

**Nunca criar componente customizado sem antes verificar o DS.** O que parece não existir às vezes existe com outro nome.

**Nunca usar cores hardcoded.** Todo fill, stroke e text color via token de variável. Nunca `{ r: 0.1, g: 0.2, b: 0.3 }` direto.

**Nunca usar fontSize hardcoded.** Sempre via text style do DS.

**Nunca usar padding hardcoded fora do grid de 8px.** Padding de 10px, 15px, 22px: invalida a consistência do grid.

**Nunca avançar para prototipação com componente marcado como ⚠️ não resolvido.** Verificar no Figma antes, não durante.

---

## Contexto herdado

Esta skill herda contexto de `product-designer-zoppy` e `zoppy-figma-mcp`. O output desta skill alimenta obrigatoriamente `zoppy-prototyping-figma`.

**Ao concluir o DS Check**, sinalize:
> "DS Check concluído. Lista de componentes aprovados e tokens mapeados. Próximo passo: `zoppy-prototyping-figma` para especificar todos os estados e executar no Figma."
