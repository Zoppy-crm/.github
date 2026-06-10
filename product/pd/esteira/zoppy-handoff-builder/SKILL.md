---
name: zoppy-handoff-builder
description: >
  Skill de handoff para engenharia da Zoppy. Última etapa da esteira. Recebe o protótipo aprovado na página WIP do Figma e produz documentação completa e acionável para o time de dev: anotações no Figma via MCP, página de spec no Notion linkada ao PRD, e checklist de entrega rastreado. O dev não deve precisar perguntar nada após ler essa documentação. Acionar quando: "protótipo aprovado", "vou passar pro dev", "escrever a spec técnica", "fazer handoff", "documentar para engenharia", "preciso passar para o dev", "frames aprovados na WIP".
---

# Skill: Handoff Builder — Zoppy

Você transforma o protótipo aprovado em documentação acionável para o time de engenharia.

**Critério de qualidade:** o dev não deve precisar perguntar nada após ler o handoff.

**Princípio:** handoff não é sobre explicar o design — é sobre eliminar ambiguidade na implementação. A diferença entre um handoff bom e um ruim é medida pelo número de perguntas que o dev precisa fazer depois.

---

## Posição no fluxo

```
Prototipação → Handoff ← VOCÊ ESTÁ AQUI
```

**Entrada:** protótipo aprovado na página WIP do Figma + briefing original (critérios de aceitação)
**Saída:** anotações no Figma (via MCP) + página de spec no Notion + checklist de entrega

---

## Passo 1 — Leitura do protótipo via Figma MCP

Antes de documentar, execute no Figma:

1. Listar todos os frames da página WIP — nome, tamanho, posição
2. Mapear os estados — quantos estados por tela? Quais?
3. Identificar componentes usados — instâncias do DS, construções via Auto Layout
4. Identificar tokens aplicados — variáveis de cor, text styles
5. Identificar fluxos de navegação — quais ações levam para quais frames?

Se algum frame estiver incompleto, sem nome descritivo ou com componente não identificado — sinalizar antes de documentar.

---

## Passo 2 — Anotações no Figma (via MCP)

Para cada tela ou grupo de telas, criar anotação inline posicionada à direita do frame (+32px no eixo X).

### Estrutura da anotação por tela

```
TELA: [Nome do frame]
Estado: [Default / Loading / Erro / Vazio / Sucesso / etc.]
Gatilho: [o que faz esse estado aparecer]

COMPORTAMENTOS
• [ação do usuário] → [o que acontece]
• [ação do usuário] → [o que acontece]

LÓGICA CONDICIONAL
• Se [condição X] → [mostrar/esconder/mudar Y]
(omitir seção se não houver lógica condicional)

EDGE CASES
• [situação limite] → [comportamento esperado]
• [dado vazio] → [o que mostrar]
• [dado longo] → [como truncar]

TOKENS
• Background: [Surface/token]
• Texto principal: [Text/token] — [text style]
• Borda: [Border/token] — [peso]px

COMPONENTES DS
• [Componente] — variante: [variante] — prop: [valor]
```

### Código base para criar anotação via `Figma:use_figma`

```javascript
// Ler figma-use e zoppy-figma-mcp antes de executar
const page = figma.root.children.find(p => p.name.includes('WIP'));
await figma.setCurrentPageAsync(page);

async function makeAnnotation(targetFrame, lines) {
  await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
  await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });

  const box = figma.createFrame();
  box.name = `Anotação — ${targetFrame.name}`;
  box.layoutMode = 'VERTICAL';
  box.itemSpacing = 6;
  box.paddingTop = box.paddingBottom = box.paddingLeft = box.paddingRight = 16;
  box.cornerRadius = 8;
  box.fills = [{ type: 'SOLID', color: { r: 0.98, g: 0.98, b: 1 } }];
  box.x = targetFrame.x + targetFrame.width + 32;
  box.y = targetFrame.y;
  page.appendChild(box);

  for (const { text, bold } of lines) {
    const t = figma.createText();
    t.fontName = { family: 'Inter', style: bold ? 'Bold' : 'Regular' };
    t.fontSize = bold ? 11 : 12;
    t.characters = text;
    t.fills = [{ type: 'SOLID', color: bold
      ? { r: 0.486, g: 0.231, b: 0.929 }  // roxo Zoppy para títulos
      : { r: 0.26, g: 0.29, b: 0.34 }      // cinza para corpo
    }];
    box.appendChild(t);
  }
  box.layoutSizingHorizontal = 'HUG';
  box.layoutSizingVertical = 'HUG';
  return box.id;
}
```

---

## Passo 3 — Página de Spec no Notion

Criar página filha do PRD original no Notion com esta estrutura:

```markdown
# Handoff — [Nome da Feature]
> Status: Aprovado para dev | Data: [data] | Designer: Millena | Figma: [link WIP]

## Problema resolvido
[Problema em uma frase do briefing original]

## Hipótese implementada
[Hipótese de solução do briefing]

## Critérios de aceitação — rastreados do briefing
✓ [critério] — como verificar: [método]
✗ [critério fora de escopo] — motivo: [razão]

## Telas e estados

### [Nome do grupo de telas]
- Link Figma: [link direto para o frame]
- Estados cobertos: [Default, Erro, Vazio, Loading, Sucesso]

**Comportamentos:**
| Ação | Resultado | Frame destino |
|---|---|---|
| [ação] | [resultado] | [frame] |

**Lógica condicional:**
- Se [condição] → [fazer X]
- Se [condição] → [fazer Y]

**Edge cases:**
| Situação | Comportamento |
|---|---|
| Campo vazio | [o que mostrar] |
| Dado longo | [como truncar] |
| API offline | [fallback] |
| Sem permissão | [redirecionamento] |

**Componentes DS usados:**
| Componente | Variante | Propriedades |
|---|---|---|
| Button | Primary Filled Medium | Label: "Salvar", disabled quando inválido |

**Tokens aplicados:**
| Elemento | Token de cor | Text style |
|---|---|---|
| Background do card | Surface/Warning | — |
| Título do alerta | Text/Critical | Body Highlight |

## Microtextos aprovados
| Elemento | Texto final |
|---|---|
| Título da tela | "[texto]" |
| CTA principal | "[texto]" |
| Empty state | "[texto]" |
| Erro de API | "[texto]" |

## O que está fora do escopo desta entrega
- [item] — motivo: [razão]

## Próximos passos
- [ ] Dev estima e entra no sprint
- [ ] Design revisa implementação antes do deploy
- [ ] Métricas do briefing medidas em [prazo] dias pós-deploy
```

---

## Passo 4 — Checklist de entrega

Antes de sinalizar o handoff como completo:

**Figma:**
- [ ] Todos os frames na página WIP com nomes descritivos
- [ ] Todos os estados documentados (default, loading, erro, vazio, sucesso)
- [ ] Anotações inline criadas para cada grupo de telas
- [ ] Todos os componentes são instâncias do DS (sem componentes desconectados)
- [ ] Tokens de cor e text styles aplicados via variável (sem hardcoded)
- [ ] Fluxo de navegação legível (setas ou labels entre frames)

**Notion:**
- [ ] Página criada como filha do PRD original
- [ ] Link do Figma (WIP) na página
- [ ] Critérios de aceitação do briefing rastreados (✓ atendido / ✗ fora de escopo)
- [ ] Edge cases documentados por tela
- [ ] Microtextos finais listados
- [ ] O que está fora do escopo está explícito

**Para o dev:**
- [ ] Nenhuma pergunta aberta que o dev precisaria fazer para implementar
- [ ] Todas as lógicas condicionais documentadas
- [ ] Todos os estados de erro e vazio têm comportamento definido
- [ ] Dependências de API ou dados identificadas

---

## Bloco de Status da Etapa

```markdown
## Status da Etapa — Handoff

- **Pode avançar?** [Feature pronta para dev / Revisar antes de entregar]
- **Nível de confiança:** [Baixo / Médio / Alto]
- **O que foi entregue:**
  - Frames anotados no Figma: [lista]
  - Página Notion: [link]
  - Checklist: [completo / pendências]
- **Hipóteses que ainda precisam ser validadas:**
  - [hipóteses do briefing que só serão testadas com usuários reais pós-deploy]
- **Lacunas abertas:**
  - [o que ficou fora desta entrega e por quê]
- **Recomendação:** [Pronto para dev / Revisar / Pausar — falta X]
- **Motivo:** [1-2 linhas]
```

---

## Pós-deploy — rastreamento

Após o deploy, registrar na página Notion:

```markdown
## Resultado pós-deploy — [data]

### Métricas monitoradas (do briefing)
| Métrica | Baseline | Resultado 30 dias | Variação |
|---|---|---|---|
| [métrica] | [baseline] | [resultado] | [+/-X%] |

### Hipóteses confirmadas / refutadas
[resultado do que o briefing previa]

### Próxima iteração sugerida
[com base nos resultados]
```

---

## Anti-padrões

**Nunca entregue com estado de loading não documentado.** O dev vai implementar o que quiser.

**Nunca entregue com edge cases de dados vazios em aberto.** Todo campo que pode estar vazio precisa ter tratamento definido.

**Nunca entregue sem rastrear os critérios de aceitação do briefing.** Se o briefing dizia "taxa de erro deve cair 30%", o handoff deve dizer como isso vai ser medido.

**Nunca assuma que o dev vai abrir o Figma e entender sozinho.** O Figma mostra o visual — a documentação explica o comportamento.

---

## Contexto herdado

Herda contexto de `product-designer-zoppy`, `zoppy-figma-mcp` e `figma-use`.

**Ao concluir o Handoff**, sinalize:
> "Handoff concluído. Figma anotado, spec no Notion linkada ao PRD. Feature pronta para estimar e entrar no sprint. Agendar review de implementação antes do deploy."
