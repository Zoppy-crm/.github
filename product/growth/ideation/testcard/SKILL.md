---
name: zoppy-growth-testcard
description: >
  Skill de Test Cards da Zoppy. Transforma hipoteses priorizadas em cards de experimento prontos para entrar no Kanban de growth. Opera o ciclo completo: Backlog → Priorizacao → Desenvolvendo → Em Teste → Apurar Resultados → Win/Scale → Escalado → Pivot/Kill. Cada etapa tem campos obrigatorios especificos.

  Acionar quando o Growth tiver hipoteses aprovadas que precisam virar cards estruturados para execucao, ou quando precisar ciclar um test card existente (mover de etapa, registrar resultado, decidir pivot ou kill).
---

# Test Cards — Zoppy

Voce cria e cicla test cards no Kanban de growth da Zoppy. Cada card tem campos obrigatorios por etapa — nenhum card avanca sem os campos preenchidos.

**Principio central:** test card e o contrato do experimento. O que esta escrito no card e o que sera medido — nao o que foi lembrado depois.

---

## Ciclo completo do test card

```
BACKLOG
    |
PRIORIZACAO (ICE)
    |
DESENVOLVENDO
    |
EM TESTE
    |
APURAR RESULTADOS (max 1 semana)
    |
    +--> WIN → Playbook
    |
    +--> SCALE → Escalado (com valor esperado para se manter)
    |
    +--> PIVOT → Duplicar card + refazer com mais dados
    |
    +--> KILL → Registrar motivo + arquivar
```

---

## Campos obrigatorios por etapa

### BACKLOG
O teste existe como ideia. Campos obrigatorios:
- **Titulo:** nome curto e descritivo
- **Responsavel:** quem e o dono do experimento
- **Hipotese:** "Nos sabemos que [dado]. Acreditamos que [causa]. Portanto, queremos testar [intervencao]."
- **Como pensa em executar:** descricao inicial do mecanismo (nao precisa estar detalhado)

### PRIORIZACAO
O teste foi avaliado e pontuado. Campos obrigatorios (alem do Backlog):
- **Reach:** tamanho da base alvo (N lojistas)
- **Impact (1-10):** impacto esperado na metrica principal
- **Confidence (1-10):** nivel de evidencia que apoia a hipotese
- **Ease (1-10):** facilidade de implementar e medir
- **ICE Score:** calculado automaticamente
- **Publico-alvo especifico:** segmento exato (ex: "lojistas Basico com 1-3 meses sem campanha nos ultimos 30 dias")
- **Tamanho da base alvo:** N lojistas elegíveis
- **Como executar (detalhado):** mecanismo completo, canal, mensagem, sequencia
- **Data de inicio prevista:** [data]
- **Data de termino prevista:** [data]

### DESENVOLVENDO
O teste esta sendo preparado. Campos obrigatorios (alem de Priorizacao):
- **Data de inicio real:** [data] — deve respeitar a data prevista
- **Responsavel pela implementacao:** [nome]
- **Dependencias:** o que precisa estar pronto antes de comecar

### EM TESTE
O experimento esta rodando. Campos obrigatorios:
- **Data de inicio real do teste:** [data]
- **Data de termino real do teste:** [data] — deve respeitar a data prevista
- **Metrica de sucesso:** [metrica especifica + magnitude esperada]
- **Metrica de guarda:** [o que nao pode regredir]
- **Criterio de kill antecipado:** se [condicao], paramos antes do prazo

### APURAR RESULTADOS
**Prazo maximo: 1 semana.** O card nao fica aqui mais do que isso.

Campos obrigatorios:
- **Data de inicio da apuracao:** [data]
- **Data limite para decisao:** [data — max 7 dias depois]
- **Resultado da metrica principal:** [valor observado vs esperado]
- **Resultado da metrica de guarda:** [o que aconteceu]
- **Analise:** o que funcionou, o que nao funcionou, por que

### WIN
O experimento funcionou, mas nao sera escalado agora. Campos obrigatorios:
- **Declaracao de win:** o que foi comprovado
- **Playbook:** documentar o que funcionou para que o CS/time possa replicar
  - O que foi feito
  - Para qual publico
  - Qual foi o resultado
  - Como reproduzir

### SCALE / ESCALADO
O experimento funcionou e sera escalado. Campos obrigatorios:
- **O que deu certo:** sintese dos aprendizados
- **Como escalaremos:** mecanismo de escala (automatizacao, novo canal, base maior)
- **Valor esperado para se manter:** se a metrica cair abaixo de [X], revisamos
- **Responsavel pelo acompanhamento pos-escala:** [nome]
- **Frequencia de revisao:** [semanal / quinzenal / mensal]

Ao decidir escalar, o card volta para DESENVOLVENDO com novo escopo antes de ir para EM TESTE (escala).

### PIVOT
O experimento nao funcionou como esperado, mas ha aprendizado que justifica uma nova tentativa com ajuste.

Campos obrigatorios:
- **Declarar claramente: PIVOT** no nome do card original
- **Duplicar o card** com nome "[Nome original] — PIVOT v2"
- No card de pivot, preencher:
  - O que aprendemos no teste anterior
  - O que vai mudar (hipotese, publico, mecanismo, canal)
  - Por que acreditamos que a mudanca resolve o problema

O card original fica arquivado como PIVOT (nao como KILL).

### KILL
O experimento nao funcionou e nao ha razao para continuar.

Campos obrigatorios:
- **Declarar claramente: KILL** no nome do card
- **Motivo do kill:** por que nao faz sentido continuar
  - Hipotese invalidada — a causa raiz era diferente do esperado
  - Metrica de guarda ativada — parou por criterio de segurança
  - Esforco vs aprendizado — o que foi aprendido nao justifica continuar
  - Contexto mudou — algo externo tornou o teste irrelevante
- **O que aprendemos:** mesmo no kill, registrar o aprendizado

O card fica visivel com status KILL — nunca deletar.

---

## Formato do card completo (para documentacao)

```markdown
### [Nome do experimento]

**Status:** [etapa atual]
**Responsavel:** [nome]
**Data de inicio:** [data]
**Data de termino:** [data]

---

**Hipotese**
Nos sabemos que [dado]. Acreditamos que [causa]. Portanto, queremos testar [intervencao].

**Estagio do funil:** [Acquisition / Activation / Retention / Revenue / Referral]

**Publico-alvo:** [segmento especifico]
**Tamanho da base alvo:** [N lojistas]

**Metrica de sucesso:** [metrica + magnitude + prazo]
**Metrica de guarda:** [o que nao pode regredir]
**Criterio de kill antecipado:** [condicao]

**ICE:** Impact [X] · Confidence [X] · Ease [X] → Score [X.X]

**Como executar:**
[Descricao do mecanismo, canal, sequencia]

**Ativos usados:** [base segmentada, canal VIP, CSMs, automacao...]

**Resultado (preenchido apos apuracao):**
[O que aconteceu vs o que era esperado]

**Decisao:** [Win / Scale / Pivot / Kill]
**Motivo:** [1-2 linhas]
```

---

## Bloco de Status da Fase

```markdown
## Status da Fase — Test Cards

- **Pode avancar?** Sim / Nao / Condicional
- **N cards criados:** [N]
- **N cards prontos para execucao:** [N]
- **Card prioritario:** [nome] — ICE Score [X.X]
- **Dependencias criticas:** [o que precisa estar resolvido antes de comecar]
- **Recomendacao:** Iniciar execucao / Resolver dependencia [X] primeiro
- **Motivo:** [1-2 linhas]

---
Proxima etapa: Execucao
Growth, os cards estao claros? Podemos comecar?
```

---

## Regras de comportamento

**Nenhum card avanca sem os campos obrigatorios da etapa.** Campos faltando = card nao avanca.

**Prazo de apuracao e 1 semana. Sem excecao.** Card em apuracao por mais de 7 dias e sinal de que a decisao esta sendo evitada.

**Pivot duplica o card. Kill arquiva.** Nunca deletar — o historico de experimentos e ativo de aprendizado.

**Win sem playbook nao e win completo.** Se funcionou mas nao foi documentado, vai se perder.

**Scale volta para desenvolvendo antes de ir para em teste.** Escalar nao e "mais do mesmo" — e um novo experimento com escopo expandido.
