---
name: zoppy-customer-intelligence
description: >
  Skill de Customer Intelligence da Zoppy. Antecipa as dúvidas, confusões e objeções que o lojista vai ter em cada tela antes de você precisar descobrir via CS ou suporte. Levanta proativamente o que vai gerar ticket, onde o lojista vai travar, o que ele vai interpretar errado e onde precisa de ajuda contextual. Acionar no briefing e na prototipação de qualquer tela nova, ou quando mencionar "suporte", "lojista pergunta", "CS reclama", "dúvida frequente", "lojista não entende", "confusão entre", "o que vai gerar ticket".
---

# Skill: Customer Intelligence — Zoppy

Você conhece o lojista antes de ele abrir a boca. Cada tela que entra em produção sem passar por esta skill é uma aposta de que o lojista vai entender sozinho — e essa aposta perde com frequência.

---

## Banco de dúvidas reais por módulo

Dúvidas coletadas de padrões de CS, suporte e comportamento do lojista na plataforma.

---

### Giftback

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "Qual a diferença entre o desconto que o cliente ganha e o limite de desconto?" | 🔴 Alta | 🔴 Alto — configura errado e o Giftback não funciona | Labels com impacto + preview calculado + tooltip diferenciando os dois |
| "Quando o Giftback é enviado pro meu cliente?" | 🟡 Média | 🟡 Médio — gera ansiedade pós-configuração | Timeline visual da jornada do cupom |
| "Meu cliente recebeu mas não conseguiu usar" | 🟡 Média | 🔴 Alto — lojista culpa o produto | Validação dos parâmetros antes de salvar |
| "O Giftback está ativo mas não aparece no relatório" | 🟡 Média | 🟡 Médio — frustração com atribuição | Status claro de "ativo desde [data]" + explicação de quando aparece nos relatórios |
| "Posso mudar o percentual depois de ativar?" | 🟢 Baixa | 🟢 Baixo | Indicar editabilidade nos campos |
| "O desconto sai do meu bolso ou da Zoppy?" | 🔴 Alta (novos lojistas) | 🔴 Alto — pode gerar churn imediato | Explicar claramente na configuração que é desconto do lojista |

---

### Campanhas

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "O que é 'Em risco'? Quem são esses clientes?" | 🔴 Alta | 🟡 Médio — segmenta errado | Descrição em linguagem de lojista ao lado de cada segmento no momento da seleção |
| "Quantas vezes esse cliente vai receber minha mensagem?" | 🔴 Alta | 🔴 Alto — medo de irritar cliente | Mostrar frequência de envio por cliente na tela de seleção de público |
| "A campanha foi enviada? Como sei?" | 🟡 Média | 🟡 Médio | Status em tempo real: "enviando", "enviado", "X entregues" |
| "Posso cancelar depois de agendar?" | 🟡 Média | 🟢 Baixo | Botão de cancelar visível em campanhas agendadas |
| "Diferença entre campanha e mensagem automática?" | 🔴 Alta | 🔴 Alto — configura a coisa errada | Explicação contextual no início de cada fluxo de criação |
| "Por que alguns clientes não receberam?" | 🟡 Média | 🟡 Médio | Relatório de falha de entrega com motivo em linguagem de lojista |

---

### Fluxo de Automações

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "Essa mensagem vai disparar toda vez que o cliente fizer X?" | 🔴 Alta | 🔴 Alto — spam involuntário | Limite de envio por cliente visível na configuração do gatilho |
| "Posso ter várias automações ativas ao mesmo tempo?" | 🟡 Média | 🟡 Médio | Lista de automações ativas com status |
| "Como sei se a automação está funcionando?" | 🔴 Alta | 🟡 Médio | Métricas de automação: X disparos este mês |
| "A automação vai enviar para clientes antigos também?" | 🟡 Média | 🔴 Alto — comportamento inesperado | Data de início da automação + quem ela afeta explicado antes de ativar |
| "Diferença entre gatilho e ação?" | 🟡 Média | 🟡 Médio | Linguagem visual: "Quando [gatilho] → faça [ação]" |

---

### Matriz RFM

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "O que eu faço com essa informação?" | 🔴 Alta | 🔴 Alto — dado sem ação = abandono | Cada segmento tem ação sugerida direta |
| "Por que meu cliente aparece em dois perfis?" | 🟡 Média | 🟡 Médio — não acontece, mas lojista acha que sim | Explicar que cada cliente pertence a um único perfil |
| "Como os clientes mudam de perfil?" | 🟢 Baixa | 🟢 Baixo | Tooltip sobre atualização automática |
| "Esse número de clientes está certo?" | 🟡 Média | 🟡 Médio — confiança nos dados | Data de última atualização visível |
| "Hibernando e Quase Hibernando — qual a diferença?" | 🟡 Média | 🟡 Médio — confusão nos perfis semelhantes | Tooltips com definição em linguagem de lojista para cada perfil |

---

### Dashboard / Relatórios

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "O que é 'Receita gerada pela Zoppy'? Por que é diferente do total?" | 🔴 Alta | 🔴 Alto — ROI não fica claro = churn | Explicação inline do que conta como receita gerada + tooltip com critérios |
| "Esse período é correto? Meu faturamento real é diferente" | 🟡 Média | 🔴 Alto — desconfiança no produto | Fonte dos dados explícita + data de sincronização |
| "Como filtro por canal específico?" | 🟢 Baixa | 🟢 Baixo | Filtros visíveis |
| "Por que o relatório de ontem é diferente do que vi hoje?" | 🟢 Baixa | 🟡 Médio | Data/hora de última atualização |

---

### WhatsApp API

| Dúvida / Confusão | Frequência | Impacto | Resposta de design |
|---|---|---|---|
| "Quanto tempo demora para o WhatsApp aprovar?" | 🔴 Alta | 🟡 Médio | Estimativa de prazo em cada etapa + o que fazer enquanto espera |
| "Minha conta foi bloqueada — o que faço?" | 🟡 Média | 🔴 Alto | Guia de resolução inline + contato com suporte imediato |
| "Preciso de um número novo ou pode ser o meu?" | 🔴 Alta | 🟡 Médio | Requisitos de número no início do fluxo de configuração |
| "A integração sumiu depois de atualizar o app" | 🟢 Baixa | 🔴 Alto | Status de conexão sempre visível + botão de reconectar |

---

## Mapa de confusões por par de conceitos

Confusões que surgem quando dois conceitos são parecidos o suficiente para confundir.

| Par confuso | O que o lojista mistura | Como resolver no design |
|---|---|---|
| Campanha × Automação | "São dois jeitos de mandar mensagem" | Separar visualmente com ícones distintos. Explicar "pontual vs. contínuo" no início de cada fluxo. |
| Percentual de Giftback × Percentual máximo | "São a mesma coisa?" | Colocar os dois campos juntos com preview de impacto calculado em tempo real. |
| Hibernando × Quase Hibernando | "Qual é mais urgente?" | Ordem visual por urgência + tooltip com tempo de inatividade de cada um. |
| Clientes "Em Risco" × "Não Pode Perder" | "Qual ação tomar em cada um?" | Ação sugerida diferente para cada perfil na própria tela do RFM. |
| Campanha agendada × Campanha em rascunho | "Essa campanha já vai ser enviada?" | Status visual diferente + texto de status explícito: "Será enviada em [data]" vs. "Rascunho — não agendado". |
| Modelos de WhatsApp × Modelos internos | "Posso usar qualquer modelo no WhatsApp?" | Sinalizar quais modelos são aprovados para WhatsApp com badge específico. |

---

## Checklist de inteligência do cliente — por tela

Para cada tela em design, responda antes de fechar a spec:

**Dúvidas que esta tela vai gerar:**
- [ ] Alguma dúvida do banco acima é relevante para esta tela?
- [ ] Quais campos/conceitos têm maior probabilidade de gerar ticket de suporte?
- [ ] O lojista pode interpretar algum dado/texto de forma diferente do que pretendemos?

**Confusões que esta tela pode criar:**
- [ ] Algum par confuso do mapa acima aparece nesta tela?
- [ ] Há dois elementos parecidos o suficiente para confundir?
- [ ] O lojista pode achar que está fazendo X quando está fazendo Y?

**Ajuda contextual necessária:**
- [ ] Quais campos precisam de tooltip?
- [ ] Quais campos precisam de helper text (texto fixo, não só tooltip)?
- [ ] Há algum conceito novo que precisa de explicação antes de o lojista tomar uma decisão?
- [ ] Há uma ação que o lojista pode fazer sem entender as consequências?

**O que vai gerar ticket se não for resolvido:**
- [ ] Liste as 1-3 coisas mais prováveis de gerar suporte se ficarem como estão

---

## Output padrão desta skill

Ao ser acionada para uma tela ou módulo, entregue:

```markdown
## Customer Intelligence — [Módulo / Tela]

### Dúvidas com alta probabilidade nesta tela
1. [Dúvida] — Impacto: [Alto/Médio/Baixo] — Resposta de design: [ação]
2. ...

### Confusões prováveis
- [Par ou conceito] → [Como prevenir no design]

### Ajuda contextual obrigatória
- [Campo/elemento] → [Tipo de ajuda: tooltip / helper text / inline] → [Texto sugerido]

### O que vai gerar ticket se não for resolvido
1. [item mais crítico]
2. ...

### Recomendações para a spec
- [lista de mudanças de design para prevenir as dúvidas identificadas]
```

---

## Como usar esta skill

**Para tela em desenvolvimento:**
"Aplique customer intelligence na tela de [módulo/funcionalidade]. Levante: dúvidas prováveis, confusões, onde precisa de ajuda contextual e o que vai gerar ticket."

**Para revisão de protótipo pronto:**
"Revise esse protótipo sob a lente de customer intelligence. O que o lojista vai não entender? O que vai gerar suporte?"

**Para módulo específico:**
"Liste todas as dúvidas frequentes do módulo de [X] com impacto e resposta de design."
