---
name: zoppy-accessibility
description: >
  Skill de Acessibilidade da Zoppy. Garante que as interfaces funcionam para lojistas em contextos reais: celular entre atendimentos, conexão lenta, sol na tela, dislexia leve, dedo grande. Verifica contraste, touch targets, hierarquia visual, leitura de tela e estados de foco antes do handoff. Acionar na revisão de prototipação, antes do handoff, ou quando mencionar "mobile", "celular", "vendedor no painel", "contraste", "acessibilidade", "toque", "tamanho do botão".
---

# Skill: Acessibilidade — Zoppy

Acessibilidade na Zoppy não é sobre WCAG teórico. É sobre o vendedor usando o Painel do Vendedor no celular, com sol na tela, entre dois atendimentos. É sobre o lojista de 55 anos que nunca usou um CRM. É sobre conexão 3G na loja física.

---

## Contexto de uso real dos lojistas

| Persona | Contexto de uso | Implicação de design |
|---|---|---|
| **Lojista dono** | Desktop ou notebook, home office ou loja | Padrão web responsivo. Menos urgência de mobile-first para gestão. |
| **Vendedor** | Celular, loja física, entre atendimentos | Mobile-first crítico. Touch targets grandes. Ação evidente. Sem scroll infinito. |
| **Lojista de loja física** | Celular, tablet, às vezes desktop antigo | Texto grande, contraste alto, interface tolerante a erros de toque. |
| **Lojista 55+** | Celular com fonte aumentada pelo sistema | Layout que não quebra com font-scale aumentado. |

---

## Contraste — checklist obrigatório

Mínimos baseados em WCAG AA (nível mínimo aceitável para o produto Zoppy):

| Tipo de texto | Proporção mínima | Token a verificar |
|---|---|---|
| Texto normal (body, label) | 4.5:1 | Text/* sobre Surface/* |
| Texto grande (título, 20px+) | 3:1 | Text/* sobre Surface/* |
| Componentes de interface (borda de input, ícone) | 3:1 | Border / ícone sobre fundo |
| Texto sobre cor primária (Action/Primary #7B3DFF) | 4.5:1 | Branco sobre primária: ✅ 5.8:1 |

### Combinações críticas da Zoppy para verificar

| Combinação | Proporção | Status |
|---|---|---|
| Text/Neutral (#727C8C) sobre Surface/Default (#FDFDFD) | ~3.9:1 | ⚠️ Atenção — abaixo do AA para texto pequeno |
| Action/Warning (#CF7F20) sobre Surface/Default | ~3.2:1 | ⚠️ Atenção — só use para texto grande |
| Action/Success (#2DB081) sobre Surface/Default | ~3.4:1 | ⚠️ Atenção — não use para texto pequeno |
| Action/Primary (#7B3DFF) sobre Surface/Default | ~5.8:1 | ✅ |
| Action/Critical (#B91414) sobre Surface/Default | ~5.1:1 | ✅ |
| Text sobre Surface/Primary (#DCE2FF) | verificar por caso | Depende do texto |

**Regra:** nunca use cor como único indicador de estado. Erro não é só vermelho — tem ícone + texto + posição.

---

## Touch targets — padrões obrigatórios

Baseado no contexto real do Painel do Vendedor e uso mobile.

| Elemento | Tamanho mínimo | Componente DS |
|---|---|---|
| Botão primário | 44px altura | Button Medium (44px) ✅ |
| Botão secundário | 44px altura | Button Medium (44px) ✅ |
| Botão pequeno | 32px altura | Button Small — apenas desktop! Nunca mobile |
| Icon button | 44×44px | Icon Button ✅ |
| Checkbox / Radio | Área de toque 44×44px mínimo | Componentes DS |
| Toggle | 44px de altura | Toggle DS ✅ |
| Item de lista / linha de tabela | 48px altura | Table List — verificar |
| Link inline | Área de toque expandida com padding | Adicionar padding 8px vertical |

**Regra para mobile:** Button Small (32px) só em desktop. No Painel do Vendedor e qualquer tela mobile-primary, mínimo Medium (44px).

---

## Hierarquia visual sem cor

A interface precisa fazer sentido para quem tem daltonismo ou imprime em preto e branco.

**Checklist:**
- [ ] Status de erro identificável por ícone + texto (não só cor vermelha)
- [ ] Status de sucesso identificável por ícone + texto (não só cor verde)
- [ ] Status de alerta identificável por ícone + texto (não só cor laranja)
- [ ] Campos obrigatórios com asterisco (não só cor diferente)
- [ ] Links distinguíveis de texto normal por sublinhado ou peso (não só cor)
- [ ] Estado selecionado com borda ou fundo (não só cor de texto)
- [ ] Perfis RFM identificáveis por label + ícone (não só pela cor do segmento)

**Regra:** toda informação transmitida por cor deve ter um segundo canal visual.

---

## Estados de foco — teclado e leitor de tela

Para o produto web (desktop):

| Elemento | Comportamento esperado |
|---|---|
| Botões | Anel de foco visível (2px, cor Action/Primary) |
| Inputs | Borda em Action/Primary quando focado |
| Links | Anel de foco visível |
| Modais | Foco entra automaticamente no modal ao abrir |
| Modais | Foco não sai do modal enquanto estiver aberto (focus trap) |
| Dropdowns | Navegável por teclado (setas) |
| Tabs | Tab Bar navegável por teclado |

**Regra:** nunca remova o outline de foco sem substituir por alternativa visível.

---

## Texto e legibilidade

| Requisito | Parâmetro | Contexto Zoppy |
|---|---|---|
| Tamanho mínimo de body | 14px (Label) — preferível 16px (Body) | Lojista 55+ com celular |
| Comprimento de linha | 60-75 caracteres em desktop | Relatórios e dashboards |
| Espaçamento entre linhas | mínimo 1.5x o tamanho da fonte | Body: 16px → 24px line-height |
| Evitar | ALL CAPS em textos corridos | Apenas em labels curtos |
| Evitar | Itálico em blocos de texto | Apenas em ênfases pontuais |
| Evitar | Texto sobre imagem sem overlay | Especialmente em banners |

---

## Feedback não-visual (além do visual)

Para contextos onde o visual não é suficiente:

| Contexto | Recurso |
|---|---|
| Loading assíncrono | aria-live para anunciar quando conteúdo carregar |
| Erro de formulário | Focus no primeiro campo com erro após tentativa de submit |
| Sucesso de ação | Mensagem de sucesso com aria-live="polite" |
| Modais | aria-modal="true" + aria-labelledby com o título |
| Ícones sem texto | aria-label descritivo no elemento |
| Imagens decorativas | alt="" (vazio, não ausente) |
| Tabelas de dados | Headers com scope="col" ou scope="row" |

---

## Checklist de acessibilidade — antes do handoff

### Contraste
- [ ] Texto body e label passam em 4.5:1 sobre o fundo
- [ ] Texto grande (20px+) passa em 3:1
- [ ] Text/Neutral não usado em texto pequeno sobre Surface/Default
- [ ] Cores semânticas (Success, Warning) não usadas isoladas em texto pequeno

### Touch e interação
- [ ] Nenhum botão abaixo de 44px em telas mobile-primary
- [ ] Button Small restrito a desktop
- [ ] Links e ações têm área de toque mínima 44px
- [ ] Itens de lista têm altura mínima de 48px

### Cor como único canal
- [ ] Estado de erro tem ícone + texto (não só vermelho)
- [ ] Estado de sucesso tem ícone + texto (não só verde)
- [ ] Campo obrigatório tem asterisco (não só cor)
- [ ] Perfil RFM identificável sem cor

### Teclado e foco
- [ ] Todos os elementos interativos acessíveis por Tab
- [ ] Foco visível em todos os elementos interativos
- [ ] Modais têm focus trap
- [ ] Dropdowns navegáveis por teclado

### Texto
- [ ] Sem texto abaixo de 14px (Label)
- [ ] Body em 16px para textos corridos
- [ ] Sem ALL CAPS em textos com mais de 4 palavras

---

## Como usar esta skill

**Para revisão de protótipo:**
"Revise este protótipo de [tela/módulo] sob a lente de acessibilidade. Verifique: contraste, touch targets, hierarquia sem cor, e o que vai quebrar no celular."

**Para tela específica:**
"Aplique o checklist de acessibilidade na tela de [X]. Identifique falhas críticas e sugestões de correção."

**Para Painel do Vendedor:**
"Faça a revisão mobile-first do Painel do Vendedor. Priorize: touch targets, contraste em luz solar, hierarquia de ação imediata."
