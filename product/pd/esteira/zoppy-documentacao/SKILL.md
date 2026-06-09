---
name: zoppy-documentacao
description: "Skill de documentação de telas da Zoppy para handoff técnico. Acionar sempre que um protótipo estiver pronto para ser documentado antes de ir para o dev — gera anotações no Figma via MCP e página de documentação no Notion linkada ao PRD. Cobre: comportamentos por estado, lógica condicional, tokens aplicados, edge cases e critérios de aceitação rastreados do briefing. Acionar quando a designer mencionar 'documentar', 'anotar', 'handoff', 'passar pro dev', 'escrever a spec', 'criar a documentação', 'o dev precisa entender' ou 'mover para handoff'."
---

# Skill: Documentação de Telas — Zoppy

Você gera documentação técnica de handoff a partir de protótipos prontos na página WIP do Figma. Seu output tem dois destinos simultâneos: anotações diretamente nos frames do Figma (via MCP) e uma página de documentação no Notion linkada ao PRD da demanda.

O dev não deve precisar perguntar nada depois de ler essa documentação.

---

## Posição no fluxo de feature

Esta skill é a **Fase 5** do fluxo de feature da Zoppy.

```
Fase 1 — Abertura (criar pasta + duplicar template)
Fase 2 — zoppy-briefing
Fase 3 — Wireframe
Fase 4 — zoppy-prototipacao + zoppy-figma-mcp
Fase 5 → zoppy-documentacao ← VOCÊ ESTÁ AQUI
         ↓ gera anotações no Figma + página de handoff no Notion
         ↓ mover frames aprovados para página ✅ Final
Fase 6 — Atualizar telas originais pós-deploy
```

**Onde documentar:**
- Figma: anotações na página `🚧 WIP — [Feature]` do arquivo `Feature — [Nome]`
- Notion: página linkada ao PRD
Consulte `zoppy-feature-workflow` para o fluxo completo.

---

## Divisão de trabalho

| Esta skill faz | Designer revisa e aprova |
|---|---|
| Lê os frames WIP via Figma MCP | Confirma se a lógica está correta antes de publicar |
| Gera anotações nos frames (Figma) | Ajusta textos que precisam de contexto de negócio |
| Gera página de documentação (Notion) | Linka ao PRD e notifica o dev |
| Rastreia critérios de aceitação do briefing | Confirma quais foram atendidos |
| Lista tokens e componentes por frame | Verifica se instâncias estão corretas no Figma |

---

## Entrada aceita

- **Frame ou página WIP pronta** — URL do Figma ou node ID específico
- **Briefing aprovado** (output da `zoppy-briefing`) — para rastrear critérios de aceitação
- **"Documenta o [módulo/fluxo]"** — busca os frames WIP correspondentes e documenta todos

Se o briefing não for fornecido, documenta os frames e sinaliza que os critérios de aceitação precisam ser preenchidos manualmente.

---

## Protocolo de execução — sempre nesta ordem

### Passo 1 — Ler os frames via Figma MCP

```javascript
// Listar frames da página WIP
const wipPage = figma.root.findChild(n => n.name.startsWith("WIP"));
await figma.setCurrentPageAsync(wipPage);
const frames = wipPage.children.map(n => ({ id: n.id, name: n.name }));
```

Para cada frame, extrair:
- Nome e dimensões
- Componentes usados (instâncias do DS)
- Tokens de cor e tipografia vinculados (`boundVariables`)
- Textos presentes (copy final)
- Estrutura de camadas (children com nomes descritivos)

### Passo 2 — Gerar anotações nos frames (Figma)

Para cada frame documentado, criar um frame de anotação posicionado à direita do frame original:

```javascript
// Posicionar anotação à direita do frame
const annotation = figma.createFrame();
annotation.x = frame.x + frame.width + 48;
annotation.y = frame.y;
annotation.resize(400, 10);
annotation.name = `📋 Spec — ${frame.name}`;
annotation.layoutMode = 'VERTICAL';
annotation.primaryAxisSizingMode = 'AUTO';
annotation.counterAxisSizingMode = 'FIXED';
annotation.paddingTop = 24; annotation.paddingBottom = 24;
annotation.paddingLeft = 24; annotation.paddingRight = 24;
annotation.itemSpacing = 16;
```

**Conteúdo obrigatório de cada frame de anotação:**

1. **Nome do estado** — ex: "Toggle ON + Fluxos ativos"
2. **Quando aparece** — condição que leva o usuário a este estado
3. **Comportamentos** — lista de interações e o que acontece em cada uma
4. **Componentes** — nome do componente DS + variante usada
5. **Tokens** — cor de fundo, texto, borda com nome do token (não o hex)
6. **Copy final** — todos os textos do frame numerados
7. **Lógica condicional** — o que muda dependendo de variáveis de contexto
8. **Edge cases** — casos extremos cobertos neste frame

### Passo 3 — Criar fluxogramas de estado

Para cada grupo de frames relacionados (ex: upload, reativação, segmento), criar um fluxograma de nós mostrando as transições entre estados.

**Estrutura de cada nó:**
- Retângulo com nome do estado + sublabel opcional
- Cor por semântica: `Surface/Gray` (neutro), `Surface/Primary` (ativo), `Surface/Warning` (alerta), `Surface/Success` (sucesso), `Surface/Critical` (erro)
- Setas com label indicando a ação ou condição que dispara a transição

**Regras de posicionamento:**
- Fluxogramas ficam acima dos frames de protótipo (Y negativo)
- Um fluxograma por cenário — nunca misturar upload com reativação no mesmo diagrama
- Setas de cancelar/voltar sempre mostradas — o dev precisa saber para onde voltar

```javascript
// Nó de estado
async function stateNode(x, y, w, h, label, sublabel, fillToken, textToken) {
  const f = figma.createFrame();
  f.x = x; f.y = y; f.resize(w, h);
  f.cornerRadius = 8; f.strokeWeight = 1;
  f.layoutMode = 'VERTICAL'; f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'FIXED';
  f.paddingTop = 12; f.paddingBottom = 12;
  f.paddingLeft = 12; f.paddingRight = 12;
  f.itemSpacing = 4; f.primaryAxisAlignItems = 'CENTER'; f.counterAxisAlignItems = 'CENTER';
  await applyFillVar(f, fillToken);
  await applyStrokeVar(f, 'Border/Default');
  // adicionar textos com tokens...
  return f;
}
```

**Cores dos nós por tipo de estado:**

| Tipo | Fill token | Quando usar |
|---|---|---|
| Default / neutro | `Surface/Gray` | Estado inicial ou de passagem |
| Ativo / selecionado | `Surface/Primary` | Estado principal do fluxo |
| Alerta / atenção | `Surface/Warning` | Estado com aviso importante |
| Sucesso | `Surface/Success` | Conclusão positiva |
| Erro | `Surface/Critical` | Falha ou estado destrutivo |

### Passo 4 — Criar tabela de especificação de interações

Para cada elemento interativo dos frames (toggle, radio, botão, ESC), criar uma linha na tabela de interações com 5 colunas obrigatórias:

| Elemento | Evento | Estado anterior | Estado posterior | Side effect no sistema |
|---|---|---|---|---|
| Nome do componente | Tipo de evento (click, keydown, hover) | Estado visual antes da ação | Estado visual após a ação | Chamada de API, mutation, background job — ou "Nenhum — apenas UI" |

**Regras da tabela:**
- Side effects reais (que impactam backend) ficam em `Text/Primary` — destaque visual para o dev
- "Nenhum — apenas UI" em `Text/Neutral` — o dev sabe que não precisa de lógica backend
- ESC e click-fora sempre documentados para todos os modais
- Especificar o endpoint e os campos quando possível: `PATCH /flows/:id {active: false}`
- Background jobs documentados separadamente: `→ background job para processar período`

```javascript
const interactions = [
  // [Elemento, Evento, Estado anterior, Estado posterior, Side effect]
  ['Toggle "Ativar fluxos"', 'click (OFF→ON)', 'Modal upload aberto', 'Exibe painel de fluxos', 'Nenhum — apenas UI'],
  ['"Importar planilha"', 'click', 'Toggle ON', 'Loading', 'POST /upload → processa arquivo'],
  // ...
];
```

### Passo 5 — Criar frame de índice na página WIP

No topo da página, criar um frame de índice que lista todos os estados documentados:

```javascript
const index = figma.createFrame();
index.name = '📑 Índice — Activation Date';
index.x = 0; index.y = -400; // acima dos frames
```

Conteúdo do índice:
- Nome da demanda
- Link para o PRD no Notion
- Data de documentação
- Lista de todos os estados com número, nome e status (WIP / Pronto para handoff)
- Checklist de critérios de aceitação do briefing

### Passo 6 — Gerar documentação no Notion

Criar página no Notion com esta estrutura exata:

```
# [Nome da demanda] — Documentação de Handoff

> Status: Pronto para dev
> Figma: [link direto para página WIP]
> PRD: [link para o PRD]
> Data: [data]
> Designer: [nome]

---

## Visão geral
[Problema que resolve + solução implementada em 2-3 linhas]

## Estados implementados
[Tabela com: número · nome do estado · quando aparece · arquivo Figma]

## Por estado

### [Nome do estado]
**Quando aparece:** [condição]
**Componentes:** [lista]
**Tokens:** [lista]
**Comportamentos:**
- [ação] → [resultado]
**Copy:**
- [elemento]: "[texto]"
**Lógica condicional:**
- Se [condição]: [comportamento]
**Edge cases cobertos:**
- [caso]: [tratamento]

---

## Critérios de aceitação
[Tabela rastreada do briefing: critério · atendido? · como verificar]

## Checklist de QA para o dev
[ ] ...
```

---

## Formato das anotações no Figma

### Estilo visual das anotações

Os frames de anotação usam o token `Surface/Primary` (#DCE2FF) como fundo — diferenciado visualmente dos frames de protótipo (brancos) para não confundir o dev.

```javascript
// Importar estilos antes de criar anotações
const styleKeys = {
  'Body Highlight': '3b6ffd3b68166f75e6114f196f305beb83617f63',
  'Body small':     'bf57ca8eeb7d264b04eacf2aa3ee422de8de031a',
  'Label':          '529ccbd729c4ab7beda29b02a509a8ea0b19ec48',
  'Caption':        '0b577becb4a3b7eac64685da033b28bd4f4fd01a',
};
const TS = {};
for (const [name, key] of Object.entries(styleKeys)) {
  const s = await figma.importStyleByKeyAsync(key);
  if (s) TS[name] = s.id;
}

// Fundo da anotação
const V_PRIMARY_SURFACE = 'VariableID:108f61ecbce76b077622d48f565882afb5a1fa00/260:51';
const v = await figma.variables.getVariableByIdAsync(V_PRIMARY_SURFACE);
annotation.fills = [figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', v
)];
```

### Seção dentro do frame de anotação

Cada seção tem um label de categoria + conteúdo:

```javascript
async function annotationSection(title, content, width) {
  const section = figma.createFrame();
  section.resize(width, 10);
  section.layoutMode = 'VERTICAL';
  section.primaryAxisSizingMode = 'AUTO';
  section.counterAxisSizingMode = 'FIXED';
  section.fills = [];
  section.itemSpacing = 4;

  // Label da seção (ex: "QUANDO APARECE", "COMPONENTES")
  await figma.loadFontAsync({ family: 'Inter', style: 'Semi Bold' });
  const label = figma.createText();
  label.fontName = { family: 'Inter', style: 'Semi Bold' };
  label.fontSize = 10;
  label.characters = title.toUpperCase();
  label.fills = [{ type: 'SOLID', color: { r: 0.482, g: 0.239, b: 1 } }];
  if (TS['Caption']) label.textStyleId = TS['Caption'];
  section.appendChild(label);

  // Conteúdo
  await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
  const body = figma.createText();
  body.fontName = { family: 'Inter', style: 'Regular' };
  body.fontSize = 12;
  body.characters = content;
  body.fills = [{ type: 'SOLID', color: { r: 0.165, g: 0.208, b: 0.271 } }];
  body.textAutoResize = 'HEIGHT';
  body.resize(width, body.height);
  if (TS['Body small']) body.textStyleId = TS['Body small'];
  section.appendChild(body);

  return section;
}
```

---

## O que documentar por tipo de frame

### Frames de modal/dialog

Documentar obrigatoriamente:
- Gatilho de abertura (qual ação do usuário abre este modal)
- Comportamento ao fechar (X, ESC, clique fora)
- Pré-seleção de opções (qual radio/toggle vem selecionado por padrão e por quê)
- Ação do CTA principal → o que acontece no sistema
- Ação do CTA secundário (cancelar) → estado em que a tela retorna
- Persistência de estado (o modal fecha e reabre no mesmo estado ou reseta?)

### Frames de estado vazio / loading / error

Documentar obrigatoriamente:
- Condição exata que aciona este estado
- Duração máxima do loading (timeout)
- O que acontece se o loading não terminar
- CTA do empty state → onde leva
- CTA do error → retry automático ou manual?

### Frames com lógica condicional

Documentar obrigatoriamente:
- Todas as variáveis que mudam o estado visual
- O valor default de cada variável
- A hierarquia de prioridade quando múltiplas condições são verdadeiras

Exemplo do projeto Activation Date:
```
Painel de fluxos (upload):
- SE toggle=OFF → painel oculto
- SE toggle=ON e nenhum fluxo ativo → empty state do painel
- SE toggle=ON e fluxos ativos e todos registros elegíveis → lista + alert info
- SE toggle=ON e fluxos ativos e registros mistos → lista com pills warning + alert warning
- Prioridade: toggle > fluxos ativos > elegibilidade dos registros
```

### Frames com alerts

Para cada alert, documentar:
- Tipo (Info / Warning / Critical / Success) e por quê esse tipo
- Dismissível ou permanente — e por quê
- Se permanente: quando some (só quando a condição muda? nunca?)
- Copy final com variáveis dinâmicas marcadas: `[N] registros` → N = count do backend

---

## Checklist antes de publicar a documentação

Executar antes de mover qualquer frame para a seção Handoff:

```
[ ] Todos os frames têm frame de anotação à direita
[ ] Cada anotação tem: quando aparece · componentes · tokens · copy · lógica
[ ] Fluxograma criado para cada grupo de estados relacionados
[ ] Tabela de interações cobre todos os elementos clicáveis + ESC/click-fora
[ ] Side effects de backend identificados na tabela (endpoint + campos quando possível)
[ ] Frame de índice criado no topo da página WIP
[ ] Nenhum texto de anotação tem "[preencher]" ou similar em aberto
[ ] Todos os critérios de aceitação do briefing foram mapeados (atendido/não atendido)
[ ] Página no Notion criada e linkada ao PRD
[ ] Link do Figma WIP está na página do Notion
[ ] Dev foi notificado que a documentação está pronta
```

---

## Raciocínio em cadeia

Antes de gerar qualquer documentação, execute internamente:

1. Quais frames estão na WIP? Todos estão prontos ou algum ainda é rascunho?
2. O briefing foi fornecido? Tenho os critérios de aceitação para rastrear?
3. Algum frame tem lógica condicional complexa que precisa de documentação extra?
4. Há edge cases mapeados no checklist que não aparecem em nenhum frame? (faltam frames)
5. Os textos nos frames são o copy final ou placeholders?

Mostre brevemente antes de executar:
> **Leitura dos frames:** [N frames encontrados · lógica mais complexa identificada · o que vai precisar de atenção especial]

---

## Anti-padrões

**Nunca documentar frames rascunho.**
Se um frame tem texto placeholder ("[título aqui]") ou componente sem instância real, não documentar — sinalizar para o designer finalizar primeiro.

**Nunca usar hex nas anotações de token.**
Escrever `Surface/Gray` — não `#F2F5F9`. O dev trabalha com tokens, não com hex.

**Nunca descrever o visual — descrever o comportamento.**
"Botão roxo com texto branco" não é documentação. "CTA primário — ao clicar, abre Dialog de confirmação de desativação" é documentação.

**Nunca omitir lógica condicional.**
Se um elemento aparece em alguns estados e não em outros, a condição precisa estar explícita. "Painel aparece quando toggle está ativo" é mais útil que qualquer screenshot.

**Nunca criar documentação sem rastrear os critérios de aceitação.**
O dev precisa saber quais comportamentos são critérios de sucesso — não apenas o que fazer, mas como verificar se fez certo.

---

## Contexto herdado

Esta skill herda contexto de `product-designer-zoppy` (módulos, lojista, DS), `zoppy-briefing` (critérios de aceitação), `zoppy-prototipacao` (edge cases por módulo) e `zoppy-figma-mcp` (component keys, variable IDs, text style keys). Não reexplique — use diretamente.

O output desta skill move os frames de WIP para Handoff e notifica o dev. É o último passo antes da implementação.
