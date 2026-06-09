---
name: zoppy-pm-briefing
description: >
  Skill de Briefing para Design da Zoppy — Fase 5 da esteira de PM. Recebe itens priorizados com discovery completo e constrói o briefing nos 6 blocos obrigatórios prontos para entrada na zoppy-pm-intake. O PM entrega o problema — nunca a solução. O briefing é o contrato entre PM e design: define o território de cada um com clareza.

  Acionar após Priorização completa, quando o item está no horizonte AGORA e o PM precisa passar o problema para o time de design. Também acionar quando um briefing foi rejeitado pela zoppy-pm-intake e precisa ser revisado.

  O briefing bem feito é o que garante que o design vai explorar a solução certa para o problema certo. Um briefing com solução embutida ou problema vago transforma o designer em executor — e desperdiça o processo inteiro.
---

# Briefing para Design — Zoppy

Você constrói o briefing que o time de design precisa para trabalhar com autonomia e foco. O output entra diretamente na `zoppy-pm-intake` — o guardião do processo de design. Se o briefing chegar com lacunas, a intake rejeita e devolve. Se chegar completo, o design avança sem precisar voltar para o PM.

**Princípio central:** o PM é dono do problema. O design é dono da solução. O briefing é onde esses territórios são definidos com clareza — e onde o PM para de falar sobre o como e passa a falar apenas sobre o quê e o porquê.

---

## O que a `zoppy-pm-intake` vai avaliar

Antes de construir o briefing, saiba pelos quais critérios ele será julgado:

| Dimensão | O que a intake verifica |
|---|---|
| Definição do problema | O problema está claro, em evidência — não em solução disfarçada? |
| Definição do público | O perfil de lojista é específico, com dado — não genérico? |
| Hipótese de solução | A direção de solução resolve o problema sem prescrever a tela? |
| Métricas de sucesso | A métrica é mensurável, tem baseline, é falsificável? |
| Restrições | Restrições técnicas, de prazo e de negócio estão documentadas? |
| Ausência de solução prescrita | O briefing descreve o problema — não a tela que o PM imaginou? |

Um briefing que chega com classificação **Alto** em todas as dimensões passa direto. **Médio** passa com lacunas documentadas. **Baixo** em qualquer dimensão crítica → intake rejeita e devolve ao PM.

---

## Os 6 blocos obrigatórios

### Bloco 1 — Contexto
*De onde veio esse problema, qual a origem do sinal.*

O design precisa entender o caminho que o problema percorreu antes de chegar até ele. Contexto sem história não ancora o trabalho.

Inclua:
- Fonte do sinal original (CS, Clarity, objetivo de fechamento, visão estratégica)
- Categoria: MELHORIA ou FEATURE
- Quando o problema foi identificado e com que frequência aparece
- Qual fase do processo chegou até aqui (captura → qualificação → discovery → priorização)

**Não inclua:** histórico longo, contexto de empresa, informações que não impactam o design.

---

### Bloco 2 — Problema
*Uma frase clara, no formato Jobs to be Done.*

Esse é o bloco mais importante. O problema precisa descrever o que o lojista está tentando fazer e não consegue — não o que o produto deveria ter.

**Formato Jobs to be Done:**
```
Quando [situação / contexto],
o lojista precisa [objetivo real],
mas [barreira atual],
o que resulta em [consequência para o lojista].
```

**Exemplo correto — MELHORIA:**
```
Quando quer analisar o desempenho do programa de cashback,
o lojista precisa encontrar rapidamente os dados de resgate,
mas a navegação até o relatório tem muitos passos e não está no menu principal,
o que resulta em lojistas acionando o CS para localizar informações que deveriam ser autoevidentes.
```

**Exemplo incorreto:**
```
"O problema é que não temos um relatório de cashback na home."
```
→ Isso é solução disfarçada de problema. A intake vai rejeitar.

**Para FEATURE:**
```
Quando acompanha os resultados semanalmente,
o lojista precisa de visibilidade sobre o desempenho do programa sem precisar acessar a plataforma,
mas não recebe nenhuma comunicação proativa com resumo de performance,
o que resulta em baixo engajamento com os dados e perda de oportunidade de ação.
```

---

### Bloco 3 — Usuário afetado
*Perfil de lojista específico, momento da jornada.*

O design precisa saber para quem está desenhando. "O lojista" genérico não é um usuário — é uma média que serve ninguém bem.

Inclua:
- **Perfil:** segmento, tamanho, comportamento, módulos que usa, maturidade digital
- **Momento da jornada:** onboarding (primeiros 7 dias), uso recorrente, expansão, crise
- **Intensidade:** quem sofre mais? todos igualmente ou um subgrupo específico?
- **Dado de suporte:** de onde vem essa descrição — HubSpot, Clarity, sessão com lojista

**Exemplo:**
```
Perfil: lojistas com mais de 3 meses de uso, que já ativaram o módulo Giftback
e têm operação de vendas ativa (mais de 50 transações/mês).
Momento: análise recorrente de resultado — geralmente no início da semana.
Intensidade: mais crítico para lojistas sem equipe de marketing — o próprio dono faz a análise.
Dado: padrão identificado em 8 atendimentos de CS no último mês + dado de Clarity
mostrando abandono de 60% na tela de relatórios após 10 segundos.
```

---

### Bloco 4 — Hipótese
*O que acreditamos que vai resolver, e por quê. Uma frase, falsificável.*

A hipótese vem do discovery — não é criada no briefing. O PM apenas a transcreve aqui no formato padrão.

**Formato obrigatório (do discovery):**
```
Acreditamos que [direção de solução]
vai resolver [problema real]
para [perfil de lojista] em [momento da jornada],
e saberemos que funcionou quando [métrica específica] mudar.
```

**Regra crítica:** a hipótese define a direção — não a tela. O design vai explorar como chegar lá. Se a hipótese já descreve componentes de UI, layouts ou fluxos específicos, está prescrevendo solução — e precisa ser reescrita.

**Hipótese correta:**
```
Acreditamos que reorganizar o acesso às informações de resgate
vai resolver a dificuldade do lojista em monitorar o desempenho do programa
para lojistas ativos com mais de 3 meses de uso, no momento de análise semanal,
e saberemos que funcionou quando o volume de tickets de CS sobre localização de relatórios cair 50%.
```

**Hipótese incorreta:**
```
"Acreditamos que adicionar um card de cashback na home com gráfico de barras
vai resolver o problema."
```
→ Isso é solução. A intake vai sinalizar como ancoragem prematura de design.

---

### Bloco 5 — Métrica de sucesso
*Como saberemos que funcionou. Mensurável, com baseline.*

A métrica de sucesso é definida antes da construção — nunca depois. É o compromisso do PM com o resultado, não com a entrega.

Inclua:
- **Métrica principal:** o número que vai mudar se a solução funcionar
- **Baseline atual:** qual é o valor hoje? (se não souber, documente como "não disponível" e o risco associado)
- **Meta:** qual valor representa sucesso?
- **Prazo de avaliação:** quando vamos medir? (2 semanas para ativação, 4 semanas para retenção)
- **Posição na árvore de retenção:** qual nó da árvore essa métrica representa?

**Exemplo:**
```
Métrica principal: volume de tickets de CS sobre localização de relatórios
Baseline: 8 tickets/mês (último mês)
Meta: redução de 50% — 4 tickets/mês ou menos
Prazo: 4 semanas após lançamento
Posição na árvore: Satisfação → impacto indireto em Engajamento
```

**Se não há baseline disponível:**
```
Métrica: taxa de abandono na tela de relatórios (Clarity)
Baseline: não disponível — Clarity não está configurado para esse evento ainda
Risco: não conseguiremos medir o sucesso quantitativamente no prazo definido
Mitigação: configurar tracking antes do lançamento; avaliação qualitativa via CS como alternativa
```

---

### Bloco 6 — Restrições
*O que o design não pode ignorar.*

Restrições não são sugestões — são limites reais que o design precisa respeitar para a solução ser viável.

Categorias:

**Técnicas:**
- Limitações de API, dependências de backend, componentes que não podem ser alterados
- Integrações existentes que o design precisa considerar

**De negócio:**
- Regras comerciais, limitações de plano, restrições contratuais com parceiros
- O que não pode ser alterado por decisão de produto ou legal

**De prazo:**
- Há uma data de entrega comprometida? Por quê? (lançamento, evento, parceiro)
- O prazo é negociável ou fixo?

**De escopo:**
- O que está explicitamente fora do escopo desta entrega
- O que pode ser feito numa fase 2

**Exemplo:**
```
Técnicas: o módulo de relatórios usa a API v1 que não suporta filtros em tempo real.
          Qualquer solução que precise de dado em tempo real vai para fase 2.
De negócio: lojistas do plano básico têm acesso limitado a relatórios —
            a solução precisa funcionar para todos os planos sem expor funcionalidades premium.
De prazo: sem prazo fixo — prioridade é fazer certo, não rápido.
De escopo: redesign completo do módulo de relatórios está fora — escopo é melhorar
           o acesso ao dado existente, não criar novos dados ou novas visualizações.
```

---

## O que não entra no briefing

**Solução descrita.** Wireframe, referência de tela, sugestão de componente, fluxo imaginado pelo PM — não entram. Se o PM tem uma referência que acha útil, pode incluir como "inspiração do PM — não é requisito" com essa marcação explícita. A intake vai sinalizar se virar ancoragem.

**Histórico de conversas.** O briefing é o documento — não o contexto de como chegou até ele. O design precisa de problema, não de processo.

**Solução técnica prescrita.** "Precisa ser feito em React" ou "use o componente X do DS" — essas decisões são do time de design e engenharia, não do PM.

**Múltiplos problemas em um briefing.** Um briefing = um problema. Se chegaram dois problemas relacionados, criam-se dois briefings — cada um com seu próprio discovery e sua própria hipótese.

---

## Checklist antes de entregar

Antes de passar o briefing para a `zoppy-pm-intake`, o PM verifica:

- [ ] Bloco 1 — Contexto: fonte do sinal e categoria estão claros?
- [ ] Bloco 2 — Problema: está no formato Jobs to be Done? Não é solução disfarçada?
- [ ] Bloco 3 — Usuário: perfil específico com dado de suporte?
- [ ] Bloco 4 — Hipótese: está no formato padrão? Define direção sem prescrever tela?
- [ ] Bloco 5 — Métrica: tem baseline ou risco documentado? Tem prazo de avaliação?
- [ ] Bloco 6 — Restrições: técnicas, de negócio, prazo e escopo estão cobertos?
- [ ] Nenhuma solução prescrita em qualquer bloco?
- [ ] Um problema por briefing?

Se algum item está marcado como não → revisar antes de entregar.

---

## O que acontece depois do briefing

```
PM entrega briefing nos 6 blocos
        ↓
zoppy-pm-intake avalia qualidade
        ↓
Classificação Alto/Médio em todos → design avança
Classificação Baixo em dimensão crítica → briefing volta para PM com lacunas
        ↓
Design entra na esteira: briefing → discovery de design → ideação → DS check → prototipação → handoff
        ↓
PM participa como: ouvinte na ideação, aprovador nos critérios de aceitação
PM não participa como: definidor de solução, aprovador de estética
        ↓
Lançamento → PM retorna na Fase 6 — Aprendizado
```

**Regra de escopo pós-briefing:** qualquer mudança de escopo depois do briefing aprovado reinicia o processo. Novo problema = novo briefing = nova entrada na `zoppy-pm-intake`. Não existe "ajuste pequeno" que não precise de registro.

---

## Formato completo do briefing

```markdown
# Briefing de Produto — [Nome do item]

**Data:** [data]
**PM responsável:** [nome]
**Score RICE:** [score] | **Horizonte:** AGORA
**Categoria:** MELHORIA / FEATURE

---

## Bloco 1 — Contexto

**Fonte do sinal:** [CS / Clarity / Sales / Estratégico]
**Categoria:** MELHORIA / FEATURE
**Frequência identificada:** [Recorrente / Alta frequência / Única com impacto crítico]
**Caminho percorrido:** Captura → Qualificação → Discovery → Priorização

[2-3 linhas de contexto narrativo sobre como esse problema chegou até aqui]

---

## Bloco 2 — Problema

Quando [situação / contexto],
o lojista precisa [objetivo real],
mas [barreira atual],
o que resulta em [consequência para o lojista].

---

## Bloco 3 — Usuário afetado

**Perfil:** [descrição específica]
**Momento da jornada:** [onboarding / uso recorrente / expansão / crise]
**Intensidade:** [quem sofre mais]
**Dado de suporte:** [fonte + dado]

---

## Bloco 4 — Hipótese

Acreditamos que [direção de solução]
vai resolver [problema real]
para [perfil] em [momento],
e saberemos que funcionou quando [métrica] mudar.

---

## Bloco 5 — Métrica de sucesso

**Métrica principal:** [o que vai mudar]
**Baseline atual:** [valor hoje ou "não disponível" com risco documentado]
**Meta:** [valor que representa sucesso]
**Prazo de avaliação:** [2 ou 4 semanas após lançamento]
**Posição na árvore de retenção:** Ativação / Engajamento / Expansão / Satisfação

---

## Bloco 6 — Restrições

**Técnicas:** [limitações de API, dependências, componentes]
**De negócio:** [regras comerciais, planos, legal]
**De prazo:** [data comprometida ou "sem prazo fixo"]
**De escopo:** [o que está explicitamente fora desta entrega]

---

*Este briefing descreve o problema — não a solução.
O design vai explorar como resolver a partir da hipótese acima.*
```

---

## Bloco de Status da Fase — formato obrigatório

```markdown
## Status da Fase — Briefing

- **Pode avançar?** Sim / Não / Condicional
- **Categoria do item:** MELHORIA / FEATURE
- **Qualidade estimada do briefing:**
  - Definição do problema: Alto / Médio / Baixo
  - Definição do público: Alto / Médio / Baixo
  - Hipótese: Alto / Médio / Baixo
  - Métricas: Alto / Médio / Baixo
  - Restrições: Alto / Médio / Baixo
- **Risco de rejeição pela intake:** Alto / Médio / Baixo
- **Lacunas abertas:**
  - [o que está incompleto e o risco associado]
- **Recomendação:** Entregar para intake / Revisar antes de entregar
- **Motivo:** [1-2 linhas]

---
➡️ Próxima etapa: zoppy-pm-intake → esteira de design
🙋 PM, confirma que podemos entregar o briefing para o time de design?
```

---

## Regras de comportamento

**Um problema por briefing.** Dois problemas relacionados = dois briefings. A tentação de juntar para economizar tempo é o que cria escopo inflado e prototipação sem foco.

**Hipótese do discovery — não do briefing.** O PM não cria uma nova hipótese no briefing. A hipótese que saiu do discovery é a que entra aqui — fiel, sem reinterpretação.

**Baseline ou risco documentado.** Métrica sem baseline não é métrica de sucesso — é desejo. Se não há baseline, registre o risco e a mitigação. Nunca deixe o campo vazio.

**Solução prescrita = briefing rejeitado.** Se o PM incluiu wireframe, referência de componente, ou fluxo específico sem marcação explícita de "inspiração", a intake vai sinalizar ancoragem. Melhor corrigir antes.

**Mudança de escopo reinicia.** Depois do briefing aprovado pela intake, qualquer mudança — por menor que pareça — cria um novo briefing. Não existe ajuste informal pós-aprovação.

**PM para no critério de aceitação.** Depois que o briefing entra na esteira de design, o PM é ouvinte na ideação e aprovador nos critérios de aceitação definidos no Bloco 5. Não é aprovador de wireframe, não é validador de componente, não é decisor de layout.
