---
name: zoppy-ux-plg
description: >
  Par propositivo da auditoria PLG (zoppy-plg-auditoria): pega uma auditoria (ou uma tela/fluxo/brief direto) e entrega o desenho da solucao - plano priorizado de melhorias, fluxo ideal proposto e specs de tela - seguindo o design system da Zoppy e o padrao de design PLG da casa.

  Acionar depois de rodar zoppy-plg-auditoria, ou quando pedir "desenhar solucao PLG", "corrigir a tela pra ativar melhor", "propor fluxo de onboarding/ativacao", "specs de tela com padrao PLG Zoppy".
---

# Skill: /ux-plg-zoppy — Design de Solução PLG (padrão Zoppy)

## O que faz
É o par propositivo do /plg: pega uma auditoria PLG (ou uma tela/fluxo/brief direto) e entrega o **desenho da solução** — plano priorizado de melhorias, fluxo ideal proposto e specs de tela — seguindo o design system da Zoppy e o padrão de design PLG da casa. O /plg diz onde dói e por quê; esta skill diz **o que construir e em que ordem**.

## Uso
/ux-plg-zoppy [caminho da auditoria /plg]        ← modo pós-auditoria (principal)
/ux-plg-zoppy [tela ou fluxo] [contexto/brief]   ← modo direto (design antes de prototipar)

## Réguas (fontes únicas — NUNCA duplicar aqui, sempre ler antes de desenhar)
1. **PLG Design Zoppy** (doc da Millena Dutra, pasta zoppy-plg-design no Drive) — a régua de DESIGN PLG: aha moments por módulo, framework de ativação por tela (5 perguntas), estrutura obrigatória de empty state, tipos de onboarding progressivo, friction points com resposta de design, checklist pré-prototipação. **A Millena é a dona da verdade de design PLG** — esta skill APLICA o padrão dela e cita a fonte; se o padrão parecer insuficiente pro caso, propor a extensão E sinalizar pra levar à dona, não inventar por fora.
2. **Brand book da Zoppy** (Drive) — identidade visual (cores, tipografia, logo, componentes). Produto Zoppy → aplica direto. Tokens concretos: puxar do brand book; na ausência, extrair do produto real em produção — **nunca inventar paleta ou componente novo** onde já existe um em produção.
3. **Playbook de Produto §1** — a régua de ENGENHARIA (tour config-driven, spotlight, preview antes de aplicar, permission-aware, progresso persistido). Toda proposta tem que ser implementável nesse motor.
4. Se o input for uma auditoria /plg, ela é a **evidência**: cada proposta referencia o achado que resolve (P0-1, P1-7…). Proposta sem achado (ou sem friction point mapeado) por trás = opinião solta, cortar.

## Princípios de proposta
**Coerência > novidade.** Reusar componente que já existe no produto (ou na Bússola/Service Copilot) antes de propor componente novo. Produto Zoppy tem que parecer UMA família.
**Copy em linguagem de lojista** ("Cliente que sumiu", não "Em risco"; benefício antes de instrução; erro vira próximo passo).
**Cada proposta mira um aha moment declarado.** Antes de desenhar, nomear qual evento de valor a mudança aproxima (se o módulo não tem aha mapeado, mapear primeiro).
**Menor mudança que resolve.** Propor o corte mínimo viável + a versão completa quando valer; nunca só a versão dos sonhos.
**Estados sempre completos**: toda tela proposta especifica os 4 estados — vazio (estrutura obrigatória do padrão Millena), carregando, erro (com instrução acionável), populado.

## Formato do entregável
1. **Plano priorizado** — tabela: proposta · achado/friction que resolve · impacto na ativação (alto/médio/baixo, amarrado ao aha) · esforço estimado (P/M/G) · ordem recomendada. Regra de ordenação: destravar o aha vem antes de polish, SEMPRE.
2. **Fluxo ideal proposto** — o passo a passo do estado futuro, com o delta explícito vs o fluxo atual e o que cada passo novo exige de backend.
3. **Specs por tela** — pra cada tela tocada: objetivo (o resultado que o lojista precisa alcançar), wireframe em texto/ASCII ou descrição estrutural, copy proposta (título, subtítulo, CTA, helper text), os 4 estados, e o componente do design system usado.
4. **Protótipo navegável (opcional, se pedido)** — HTML seguindo o brand book; entra TUDO que foi pedido, corte de escopo é discussão de produto depois.

## Encerramento
Salvar a proposta linkando a auditoria de origem.
Proposta que revelar padrão novo de design PLG (não específico do produto) → levar à Millena (dona do padrão).
