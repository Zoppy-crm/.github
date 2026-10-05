---
name: ui-and-styling
description: >
    Regras de UI dos frontends React da Zoppy: Tailwind v4 com tokens no @theme, primitivos em shared/ui
    com Radix e cva, os quatro estados de tela, mobile-first, i18n (texto só por chave de tradução),
    formatação de dinheiro e data, toasts e confirmações. Use ao montar UI, estilizar, criar primitivo,
    escrever texto de interface ou formatar valores. Triggers: "componente", "estilo", "tailwind", "cor",
    "tema", "token", "texto", "tradução", "i18n", "t(", "tabela", "moeda", "formatar", "skeleton",
    "estado vazio", "toast", "cva", "radix", "modal", "mobile", "responsivo".
---

# UI e estilo — frontends React

**Tailwind v4** (`@tailwindcss/vite`, sem `tailwind.config`: os tokens são CSS em `src/index.css`),
primitivos próprios em `src/shared/ui` com **Radix** onde o comportamento é difícil, **cva** para
variantes, `lucide-react` para ícones e `cn()` para juntar classes.

**React e Angular não se misturam.** Nada do `ui-components` (Angular) entra num app React, nem como
dependência nem como CSS. Se outro app React precisar do mesmo tema, ele vira um pacote de estilo
compartilhado só de React.

## Tokens

Tudo é variável CSS no `@theme`, para o Tailwind gerar as utilitárias.

-   **Tokens semânticos** são os que componente usa: superfícies, bordas, texto, ação primária e
    estados (sucesso, aviso, erro, informação), além de raios e sombras. Os valores seguem a cor da
    plataforma principal da Zoppy (primária `#7B3DFF`, hover `#4400D3`, fonte Inter).
-   **A paleta padrão do Tailwind é desligada** no `@theme`: só existe o que o tema declara.
-   **Nunca cor crua em componente** (`local/no-fixed-color` barra `bg-[#…]`, `[rgb(…)]` e cor literal
    em `style`). Cor nova entra no `index.css` como token, com o propósito no nome.

## Composição

1. **`shared/ui` é genérico e não conhece domínio** (botão, campo, seleção, diálogo, toast, menu, abas,
   tabela, badge, skeleton, estado vazio, alerta de falha). O que sabe o que é um agente mora na
   entidade ou na feature.
2. **Variantes vêm do `cva`**, sem malabarismo de classe no ponto de uso. Escreva o tipo das props de
   variante e anote o resultado do `cva(...)`. Classes do chamador entram por `cn()`.
3. Props são `interface` exportada com campos `readonly`; o primitivo que envolve um elemento nativo
   repassa os atributos dele.
4. **Toda tela de dados tem os quatro estados:** carregando (skeleton do layout real, com
   `role="status"` e `aria-busy`), vazio (com a ação que preenche), erro (alerta com a mensagem
   traduzida e tentar de novo quando fizer sentido) e conteúdo. Tela sem estado vazio não está pronta.
5. **Mobile-first.** Toda tela funciona em 390 px de largura; menu vira recolhível, toolbar quebra
   linha, tabela larga rola dentro de uma caixa.
6. Acessibilidade: ícone com `aria-hidden`, botão só de ícone com `aria-label`, elemento interativo é
   `button` ou `a` de verdade, foco visível pelo estilo global de `:focus-visible`. `jsx-a11y` strict é
   erro, e os specs de tela rodam o axe.

## Texto de interface: só por chave de tradução

`i18next` + `react-i18next`, **só pt-BR por enquanto**, um namespace por feature ou entidade (`common`
para palavras genéricas). As chaves são tipadas a partir do JSON pt-BR: chave que não existe quebra o
typecheck.

O lint (`i18next/no-literal-string`) barra:

-   texto e template literal com texto dentro do JSX, no app inteiro;
-   props visíveis com string fixa: `placeholder`, `aria-label`, `title`, `alt`, `label`, `description`;
-   **qualquer string com texto nas pastas de UI** (`features/*/components`, `features/*/pages`,
    `entities/*/components`, `app/layouts`, `shared/ui`): toast, texto em handler, rótulo em objeto de
    configuração.

Ficam liberadas as strings técnicas: classes, rotas (`/app/...`), chaves (`queryKey`, `id`, `key`),
variantes (`variant`, `size`, `tone`), atributos técnicos (`href`, `role`, `type`, `data-*`) e palavras
no formato de identificador. **Limitação conhecida:** dentro de um atributo de evento de tag HTML nativa
(`<button onClick={() => toast('Salvo')}>`) o plugin não valida; declare o handler no corpo do
componente e o texto passa a ser pego.

Fora de JSX, a função que monta texto recebe `t` como parâmetro. Conteúdo longo (artigos de ajuda)
mora em `content/` da feature.

## Formatação

-   **Dinheiro, data e número via `Intl`**, pelos formatadores de `shared/lib/format/`, com o locale
    resolvido e a moeda vinda do dado. Nunca `toFixed` nem "R$" montado à mão.
-   A API fala em instantes UTC (ISO); a tela fala no horário de Brasília.

## Retorno ao lojista

-   **Toast** por `useToast()`, com texto traduzido no passado, dizendo o que aconteceu.
-   **Ação destrutiva ou irreversível** passa por diálogo de confirmação que nomeia a consequência,
    nunca "Tem certeza?".
-   Tudo acima de ~400 ms mostra progresso (botão em carregamento, skeleton).
