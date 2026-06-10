---
name: zoppy-figma-mcp
description: "Skill de uso do Figma MCP para a Zoppy. Usar sempre que for executar qualquer operação no Figma via Claude — criar frames, importar componentes do DS, criar páginas, ler estrutura de arquivos, montar protótipos. Contém os padrões de código validados, as component keys do DS da Zoppy, os gotchas conhecidos e o protocolo de execução segura. Acionar quando a designer mencionar 'cria no Figma', 'executa no Figma', 'monta os frames', 'usa o MCP do Figma', 'importa os componentes', ou quando for usar o Figma:use_figma."
---

# Skill: Figma MCP — Zoppy

Você executa operações no Figma via Plugin API usando a ferramenta `Figma:use_figma`. Esta skill contém tudo que foi validado em uso real no arquivo da Zoppy.

**Regra absoluta antes de qualquer execução:**
Sempre consultar o DS via `Figma:search_design_system` antes de criar qualquer elemento visual. Se o componente existe no DS da Zoppy (`libraryName: "Design System (2024)"`), importar via `importComponentSetByKeyAsync`. Nunca recriar manualmente algo que já existe no DS — isso inclui Topbar, Menu lateral, Buttons, Alerts, Pills e qualquer outro componente listado abaixo.

---

## Posição no fluxo de feature

Esta skill executa a **Fase 4** do fluxo — dentro da página `🚧 WIP — [Feature]` do arquivo `Feature — [Nome]`.

Sempre verificar qual arquivo e qual página antes de executar. Consulte `zoppy-feature-workflow` para o fluxo completo.

---

## Arquivos da Zoppy

| Arquivo | File Key | Uso |
|---|---|---|
| Design System (2024) | `iCUju2TRogzUxwUaa9v8dt` | Fonte de componentes, tokens e variantes |
| Produto (Activation Date) | `q5wGKoXMI5JREpGSsa7dq4` | Arquivo de telas onde a execução acontece |

Biblioteca do DS:
`lk-073688517c1029e8c05e181762bda306d834b0c3003a84e15522ab4c946bf49d198b038fd57ddf8388cc5f3be25338f1743408acaad30e4b1695a5e051be7e85`

---

## Protocolo de execução — sempre nesta ordem

**0. Consultar o DS antes de criar qualquer elemento**
Chamar `Figma:search_design_system` com o nome do componente, filtrar por `libraryName: "Design System (2024)"`. Se encontrado, importar via key. Só criar manualmente o que não existir — e nesse caso, adicionar nota de substituição.

**1. Identificar a página correta**
```javascript
const pages = figma.root.children.map(p => ({ id: p.id, name: p.name }));
return pages;
```

**2. Navegar para a página**
```javascript
const page = figma.root.findChild(n => n.name === "Nome da Página");
await figma.setCurrentPageAsync(page);
```
⚠️ `figma.currentPage =` não funciona — usar sempre `setCurrentPageAsync`.

**3. Criar página nova (quando necessário)**
```javascript
const newPage = figma.createPage();
figma.root.insertChild(INDEX, newPage);
await figma.setCurrentPageAsync(newPage);
```
⚠️ `figma.root.insertChild(index, figma.createPage())` em uma linha retorna null — separar sempre.

**4. Importar componentes do DS antes de qualquer frame**
```javascript
const topbarSet  = await figma.importComponentSetByKeyAsync('af5bc75e6e23734a037bdd6cd6c414bce88b8347');
const menuOptSet = await figma.importComponentSetByKeyAsync('036b1b5eb38ff2c3bf90920cf50f0e9b3ab1157c');
const buttonSet  = await figma.importComponentSetByKeyAsync('c53e10335aa9a5747facd0ed1725c8ad3afb199e');
const alertSet   = await figma.importComponentSetByKeyAsync('56836a7296c19104d9a7bffd30c2b7195b367080');
const pillSet    = await figma.importComponentSetByKeyAsync('95c88bd34d977849a87999075836a6a0ef004c7a');
```

**5. Sempre carregar fontes antes de setar texto**
```javascript
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
await figma.loadFontAsync({ family: 'Inter', style: 'Medium' });
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });
await figma.loadFontAsync({ family: 'Inter', style: 'Semi Bold' });
```
⚠️ `'Semi Bold'` tem espaço — não é `'SemiBold'`.

---

## Component Keys do DS da Zoppy (Design System 2024)

| Componente | Key |
|---|---|
| Button | `c53e10335aa9a5747facd0ed1725c8ad3afb199e` |
| Alert (versão nova, sem typos) | `56836a7296c19104d9a7bffd30c2b7195b367080` |
| Topbar | `af5bc75e6e23734a037bdd6cd6c414bce88b8347` |
| Menu options (item do menu lateral) | `036b1b5eb38ff2c3bf90920cf50f0e9b3ab1157c` |
| Pill | `95c88bd34d977849a87999075836a6a0ef004c7a` |
| Radio Button | `b9da93cfd5ec244f53f0766b370e9b8a05b46933` |
| Icon Button | `7ceb30c7d23585fbfdfa71b4e7ed434f325db4d5` |
| Toggle | `84c8e556edecf94892674b2d24fd0a0891611cdb` |
| Table Row (State=Default/Hover) | `60edb082f27b2999af0e7f65ff3d53f95c62d291` |
| Table head | `ee13ee4a9fad62a4638d502849ac36de1416f5bf` |
| Table Line (Property 1=Default/hover) | `254e4853bba2ede20054306e8b31d8810ad7f18a` |
| Date Picker | `ab13e33c4f20c62846e2c4a110e66c120c5c49c9` |
| Checkbox | buscar via `search_design_system` query "Checkbox" |
| Selector | buscar via `search_design_system` query "Selector" |
| Dialog | buscar via `search_design_system` query "Dialog" |
| Label | buscar via `search_design_system` query "Label" |
| Pagination | buscar via `search_design_system` query "Pagination" |
| Tooltip | buscar via `search_design_system` query "Tooltip" |
| Search Bar | buscar via `search_design_system` query "Search Bar" |
| Tab option | buscar via `search_design_system` query "Tab option" |
| Switch button | buscar via `search_design_system` query "Switch button" |
| Breadcrumb | buscar via `search_design_system` query "Breadcrumb" |

**Para qualquer componente não listado:** chamar `Figma:search_design_system` antes de criar manualmente.

---

## Variantes validadas — por componente

### Topbar
```
Notificação=False, Plano=Antigo       → padrão (mais comum)
Notificação=True,  Plano=Antigo       → com badge de notificação
Notificação=False, Plano=Zoppy Coin   → com saldo de Zoppy Coin
Notificação=True,  Plano=Zoppy Coin   → saldo + notificação
Notificação=False, Plano=Skeleton     → loading
```
⚠️ O Topbar já inclui avatar, nome da empresa e uso do plano — nunca recriar esses elementos manualmente.

### Menu options (montar menu lateral empilhando instâncias)
```
State=Default,   Active=False, Icon Only=False  → item normal
State=Selected,  Active=True,  Icon Only=False  → item ativo (página atual)
State=Hover,     Active=False, Icon Only=False  → hover
State=Default,   Active=False, Icon Only=True   → menu recolhido
State=Selected,  Active=True,  Icon Only=True   → ativo em menu recolhido
```
⚠️ O menu lateral não é um componente único — é construído empilhando instâncias de Menu options.

### Button
```
Type=Primary,       Category=Filled,   Size=Medium, State=Default → CTA principal
Type=Primary,       Category=Filled,   Size=Large,  State=Default → CTA tela cheia
Type=Primary,       Category=Outlined, Size=Medium, State=Default → ação secundária
Type=Critical,      Category=Filled,   Size=Medium, State=Default → ação destrutiva
Type=Unfocus,       Category=Filled,   Size=Medium, State=Default → desabilitado
Type=Informational, Category=Filled,   Size=Medium, State=Default → ação informativa
```
⚠️ `Mobile=False` é o único valor disponível. `State=Disable` para desabilitado real.

### Alert (versão nova — key: 56836a7296...)
```
Type=Info / Warning / Critical / Success / Neutral / Primary
Content=Default / List / Details / Dismiss / Ações
```
⚠️ Key antiga com typos (`e13daabdf...`) — não usar em novos protótipos.

### Pill
```
Type=Primary / Secondary / Success / Critical / Warning / Neutral
State=Default / Hover / Selected / Disabled
Size=Large(36px) / Small(28px) / Mini(20px — evitar)
```
⚠️ Size=Default = Small. Neutral não tem Hover/Selected/Disabled.

### Radio Button
```
State=False, Type=Default   → desmarcado
State=True,  Type=Selected  → marcado
State=True,  Type=Disable   → desabilitado
Label=false / Label=true    → sem ou com label
```

### Toggle
```
State=True/False/Disable, Size=Large, Type=Default
```

### Table Row / Table head
```
Table Row: State=Default → linha em repouso | State=Hover → com cursor
Table head: componente único (não é set), w=1225 nativo — redimensionar para a largura real da tabela
Table Line: Property 1=Default / hover — separador horizontal
```
⚠️ O Table Row e Table head do DS são bases estruturais — não têm colunas fixas. Construir as células manualmente dentro deles como frames auto-layout horizontais com padding e texto Body small Semi Bold nos headers, Body small Regular nas linhas. Usar componente como wrapper, não como solução completa.

⚠️ **Padrão de tabela customizada validado** (para tabelas com colunas específicas como Analytics):
```javascript
// Header: frame HORIZONTAL com fundo Surface/Gray, cornerRadius=8
// Células: frames FIXED width com paddingLeft=12, counterAxisAlignItems=CENTER
// Linhas: frames HORIZONTAL com strokeBottomWeight=1, Border/Default
// Texto header: Body small Semi Bold + Text/Neutral
// Texto linha nome: Body small Semi Bold + Text/Default
// Texto linha dado: Body small Regular + Text/Neutral
// Pills de status: sempre dentro de célula com paddingLeft=12
```

### Date Picker
```
Type=Default → calendário completo expandido (412×416px)
```
⚠️ Date Picker é um calendário expandido — pesado para o topo de uma tela de dashboard. O padrão correto para filtros de período é: **uma Pill Secondary/Large com o período atual + seta ↓**, que abre o Date Picker como dropdown ao clicar. Não colocar o calendário sempre visível.

### Icon Button
```
Size=Small/Medium, State=Default, Type=Neutral/Primary/Dark
```

### Dialog
```
Type=Informational / Primary / Success / Warning / Critical / AI
```

### Label
```
Type=Default / Primary / Success / Critical / Warning / Informational
Bold=True / False · Size=Default(24px) / Small(20px) · Icon=False / Icon=True
```

---

## Helper universal de variante

```javascript
function getVariant(set, props) {
  return set.children.find(c =>
    Object.entries(props).every(([k, v]) => c.name.includes(`${k}=${v}`))
  );
}

// Exemplos
const topbar      = getVariant(topbarSet,  { 'Notificação': 'False', 'Plano': 'Antigo' });
const menuActive  = getVariant(menuOptSet, { State: 'Selected', Active: 'True', 'Icon Only': 'False' });
const menuDefault = getVariant(menuOptSet, { State: 'Default', Active: 'False', 'Icon Only': 'False' });
const btnPrimary  = getVariant(buttonSet,  { Type: 'Primary', Size: 'Medium', Category: 'Filled', State: 'Default' });
const alertWarn   = getVariant(alertSet,   { Type: 'Warning', Content: 'Default' });
const pillSuccess = getVariant(pillSet,    { Type: 'Success', Size: 'Small', State: 'Default' });

// Instanciar
const inst = topbar.createInstance();
inst.x = MENU_WIDTH; inst.y = 0;
frame.appendChild(inst);
```

### Setar texto em instância
```javascript
const tn = instance.findOne(n => n.type === 'TEXT');
await figma.loadFontAsync(tn.fontName);
tn.characters = 'Novo texto';
```

---

## Variable IDs do DS

```javascript
const V = {
  'Action/Primary':        'VariableID:270f546706abc3bd4cd65a17f60bc2f810d147ba/260:50',
  'Action/Critical':       'VariableID:89e2b4717c43213fa5922f7f17b089f83035e3bd/260:33',
  'Action/Disable':        'VariableID:452514f4eed39be329c2a40b3814db0565a87f95/260:38',
  'Action/Dark':           'VariableID:1a8ed0f51352394aae20c23cb188056b43449e84/260:44',
  'Text/Primary':          'VariableID:b42578be247f4263b9eb87c0943c2df66daf7dff/260:34',
  'Text/Default':          'VariableID:55ec9e59380982a06b822a336f922563c48fcb79/260:28',
  'Text/Neutral':          'VariableID:06b0e2c545b77100ca5506410a22057add2b0e2c/260:27',
  'Text/On':               'VariableID:0793c2ead0279bc62cc17b80c3a1bc23a678c546/260:19',
  'Text/Success':          'VariableID:ee72511fb4cf0fa109dace8a68aa94c6ddf7c9c5/260:14',
  'Text/Warning':          'VariableID:de8cd51112c6d61ee16bcaaa3721b4dea94bfb53/260:3',
  'Text/Critical':         'VariableID:64772b9b72b5c17fe88398e2354ddd9f04694905/260:23',
  'Text/Informational':    'VariableID:0ac8a3f01976b1bdcf855157d83814eb8deba41f/260:21',
  'Text/Disable':          'VariableID:61c22702aefe809377e887c1ce257083dc168f30/260:26',
  'Surface/Default':       'VariableID:2c8ae5604b0ad0262eb65353b36a694c65ad5245/260:55',
  'Surface/Gray':          'VariableID:ffa7208ac4325fcdac62a6ae1d6655ac2c1d029f/357:17',
  'Surface/Selected':      'VariableID:9a6b1274e7a1032b3b4b6cf5082a945a383118a4/260:52',
  'Surface/Primary':       'VariableID:108f61ecbce76b077622d48f565882afb5a1fa00/260:51',
  'Surface/Success':       'VariableID:df439154a7dfb7fd8c769dae1bce0c2f55df3017/260:41',
  'Surface/Warning':       'VariableID:cfe247c56c7c1d66613c0659fd52bb4c53adb71b/260:42',
  'Surface/Critical':      'VariableID:f6f630c3dbc3783778ba16f0881f2bd6ebfd6581/260:46',
  'Surface/Informational': 'VariableID:0a26359c2617331965e33bfc2a4bdd8a74570711/260:45',
  'Surface/Disable':       'VariableID:5033393b52372e9873ec9e6afbaf6cabf3cbf0cc/260:54',
  'Border/Default':        'VariableID:5dc65c283959e3eb7e517e42a7b21cf78bcd6af4/260:22',
  'Border/Primary':        'VariableID:4fa0a43754c724dc0a4deda1061592718d621a46/260:18',
  'Border/Success':        'VariableID:a003c2ae560625dafd885eb09ae88d780f040154/260:20',
  'Border/Warning':        'VariableID:e87349a002143faabe593f77db5257cb76ba1fdb/260:16',
  'Border/Critical':       'VariableID:4519516d359747e7503a61d7f73fa35e550c3601/260:43',
  'Border/Informational':  'VariableID:33a2ec1ecefd4c8424674e1fafd6ae19ed339fb0/260:39',
  'Background/Default':    'VariableID:db94621bbc05da9bf0c2e6e063fed7702ed1d1eb/260:11',
  'Background/Overlay':    'VariableID:c3723eafc375df64dff2e1aed9725a77b74a6ae2/260:5',
  'Icon/Primary':          'VariableID:140:4134',
  'Icon/Secondary':        'VariableID:140:4135',
  'Icon/Neutral':          'VariableID:140:4137',
  'Icon/Warning':          'VariableID:140:4138',
  'Icon/Critical':         'VariableID:140:4139',
  'Icon/Success':          'VariableID:140:4140',
  'Icon/On':               'VariableID:140:4142',
  'Icon/Disable':          'VariableID:140:4143',
  'Icon/Dark':             'VariableID:140:4136',
  'Icon/Informational':    'VariableID:140:4141',
  'TI/Label/Default':      'VariableID:140:4123',
  'TI/Stroke/Error':       'VariableID:141:4148',
  'TI/Stroke/Active':      'VariableID:141:4144',
  'TI/Stroke/Default':     'VariableID:141:4146',
};

async function applyFillVar(node, varName) {
  const variable = await figma.variables.getVariableByIdAsync(V[varName]);
  if (!variable) return;
  node.fills = [figma.variables.setBoundVariableForPaint(
    { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', variable
  )];
}

async function applyStrokeVar(node, varName) {
  const variable = await figma.variables.getVariableByIdAsync(V[varName]);
  if (!variable) return;
  node.strokes = [figma.variables.setBoundVariableForPaint(
    { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', variable
  )];
  node.strokeWeight = 1;
}
```

**Regra absoluta:** sempre usar `applyFillVar`/`applyStrokeVar`. Nunca hardcodar cores.

---

## Text Style Keys do DS

```javascript
const styleKeys = {
  'Body':                '3076e46b195c6b564fbe61bbd71a87f12163bc92',
  'Body Highlight':      '3b6ffd3b68166f75e6114f196f305beb83617f63',
  'Body small':          'bf57ca8eeb7d264b04eacf2aa3ee422de8de031a',
  'Body Large Highlight':'5543dd8aa59d34d1c60eae7c97d7dce2ff4209e5',
  'Body Large':          'c3bb0d487b1f77c148ed8b2cc8c82ced75eebbea',
  'Button':              '6f70bcaf733c3aa81704471940e7ba03c0aa4575',
  'Label':               '529ccbd729c4ab7beda29b02a509a8ea0b19ec48',
  'Small':               '6553760a8fb7b0f685dc0f83ec4703235ce59ea2',
  'Subtitle':            '26875b07eb7b66af3f3febc1c9c3be8645dd600b',
  'Caption':             '0b577becb4a3b7eac64685da033b28bd4f4fd01a',
  'Caption Highlight':   '595a4ec9483ebccc8b94c3f50fa7dede0f35d21e',
  'Medium':              'ec75260a8ca60c0ccdfccbe9515199a7138dcf62',
  'Large':               '2813491e25489239d97e633d64d540bdb14593f3',
};
```

**Mapa tamanho+peso → estilo:**
```
32px Bold       → Large           24px Bold       → Medium
20px Bold       → Small           18px Semi Bold  → Body Large Highlight
18px Regular    → Body Large      16px Regular    → Body
16px Semi Bold  → Body Highlight  16px Bold       → Button
16px Medium     → Subtitle        14px Regular    → Body small
14px Medium     → Label           12px Regular    → Caption
12px Semi Bold  → Caption Highlight
```

⚠️ **Caption raramente usada no produto.** O código faz resize para 75% do original — no produto, Caption (12px) fica ainda menor do que parece no Figma. Usar Body Small (14px) como mínimo em praticamente todos os casos. Caption só para casos muito específicos e nunca em informação principal.

**Hierarquia tipográfica validada para Analytics/Dashboards:**
```
Valor principal (número grande)  → Small (20px Bold)
Label do card                    → Body small (14px Regular) + Text/Neutral
Detalhe/subtexto do card         → Body small (14px Regular) + Text/Neutral  ← não Caption
Título de seção                  → Body (16px Regular) ou Body Highlight (16px Semi Bold)
Label de coluna de tabela        → Body small (14px Semi Bold) + Text/Neutral
Dado de linha de tabela          → Body small (14px Regular) + Text/Neutral
Nome principal na linha          → Body small (14px Semi Bold) + Text/Default
```

---

## Padrões de layout validados

```javascript
// Auto layout vertical (card, painel)
const frame = figma.createFrame();
frame.resize(WIDTH, 10);
frame.layoutMode = 'VERTICAL';
frame.primaryAxisSizingMode = 'AUTO';
frame.counterAxisSizingMode = 'FIXED';
frame.itemSpacing = 24;
frame.paddingTop = 24; frame.paddingBottom = 24;
frame.paddingLeft = 24; frame.paddingRight = 24;

// Separador
const sep = figma.createRectangle();
sep.resize(WIDTH, 1); sep.fills = [];
await applyStrokeVar(sep, 'Border/Default');
```

---

## Armadilhas conhecidas

```javascript
// ❌ Recriar Topbar ou Menu manualmente — NUNCA
const menuRect = figma.createRectangle();

// ✅ Importar do DS
const topbar = getVariant(topbarSet, { 'Notificação': 'False', 'Plano': 'Antigo' }).createInstance();

// ❌ createPage em linha única → retorna null
figma.root.insertChild(5, figma.createPage());

// ✅
const p = figma.createPage();
figma.root.insertChild(5, p);

// ❌ Setar página diretamente
figma.currentPage = page;

// ✅
await figma.setCurrentPageAsync(page);

// ❌ Texto sem loadFont
textNode.characters = 'texto';

// ✅
await figma.loadFontAsync(textNode.fontName);
textNode.characters = 'texto';

// ❌ Alert com key antiga (typos)
await figma.importComponentSetByKeyAsync('e13daabdf0519f825a22b6d86f25011687c79bdc');

// ✅ Alert com key nova
await figma.importComponentSetByKeyAsync('56836a7296c19104d9a7bffd30c2b7195b367080');

// ❌ Resize em eixo AUTO
frame.primaryAxisSizingMode = 'AUTO';
frame.resize(100, 500);

// ✅
frame.resize(1104, frame.height);

// ❌ Cores hardcoded
node.fills = [{ type: 'SOLID', color: { r: 0.482, g: 0.239, b: 1 } }];

// ✅
await applyFillVar(node, 'Action/Primary');
```

---

## Checklist antes de finalizar

```
[ ] Topbar é instância do DS (key: af5bc75e...) — não shape manual
[ ] Menu lateral usa instâncias de Menu options (key: 036b1b5e...) — não shapes
[ ] Buttons, Alerts, Pills são instâncias do DS — não shapes
[ ] Shapes sem key têm comentário de substituição
[ ] Textos usaram loadFontAsync antes de setar characters
[ ] Fills/strokes usam applyFillVar/applyStrokeVar — sem cores hardcoded
[ ] textStyleId do DS vinculado em todos os textos
[ ] Nenhum texto usa Caption (12px) — mínimo é Body small (14px)
[ ] Auto layout correto — sem tamanho fixo em eixo AUTO
[ ] figma.notify() ao final
[ ] Frame na página correta (WIP)
[ ] Nó criado no frame correto — verificar parentId após criação
[ ] IDs dos nós criados retornados e verificados antes de prosseguir
```

---

## Gotchas adicionais descobertos em uso real

```javascript
// ❌ Nós criados podem sumir entre sessões se o script rodar no frame errado
// Sempre verificar o parentId após criação:
const node = figma.createFrame();
defaultFrame.appendChild(node); // garantir parent explícito
// Não confiar que o nó foi criado dentro do frame sem verificar

// ❌ fontSize pode ser um symbol (MIXED) quando há múltiplos tamanhos no mesmo nó
// Não fazer sort por fontSize diretamente — usar:
const bySize = texts.filter(t => typeof t.fontSize === 'number').sort((a, b) => b.fontSize - a.fontSize);

// ❌ Pills com text override: findAll retorna ícones também
// Filtrar para pegar só o text label principal:
const pillText = pill.findAll(n => n.type === 'TEXT')[0]; // primeiro text é o label

// ❌ Tabela manual sem borda bottom — usar strokeWeight individual por lado:
row.strokeBottomWeight = 1;
row.strokeTopWeight = 0;
row.strokeLeftWeight = 0;
row.strokeRightWeight = 0;
// Funciona apenas se strokeAlign = 'INSIDE' estiver setado

// ❌ Card com fills sem variável — usar branco hardcoded só quando o DS de referência
// também usa hardcoded (ex: Metric container usa #fff sem variável):
card.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]; // aceitável
// Mas fills coloridos SEMPRE via applyFillVar

// ✅ Shadow padrão dos cards do DS Zoppy (Metric container):
card.effects = [{
  type: 'DROP_SHADOW',
  color: { r: 198/255, g: 193/255, b: 212/255, a: 0.4 },
  offset: { x: 0, y: 3 }, radius: 10, spread: 0,
  visible: true, blendMode: 'NORMAL'
}];
card.cornerRadius = 16;
```

---

## Contexto herdado

Esta skill complementa `product-designer-zoppy` (DS, tokens, componentes aprovados) e `zoppy-prototipacao` (spec de estados, microtextos, edge cases). Use as três juntas para execução completa no Figma.
