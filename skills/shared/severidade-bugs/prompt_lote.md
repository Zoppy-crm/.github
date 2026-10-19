# Prompt do subagente de classificação (trocar PASTA, LOTE e SAIDA)

Classifique a severidade de bugs reais da Zoppy usando o playbook vigente. Trabalho só de leitura e escrita de arquivo local: NÃO altere nada no GitHub nem no HubSpot.

Pasta de trabalho: PASTA (onde estão o lote e a saída).
- Playbook: .claude/skills/severidade-bugs/playbook.md do repo em que a sessão está (fonte oficial, skill severidade-bugs). Se não existir, use o caminho absoluto que quem te chamou passar. Leia inteiro antes de começar e siga o algoritmo da seção 6 na ordem, com as definições da seção 7. Pontos centrais: HighTouch e reincidência NÃO mudam severidade; Crítico só com os três critérios da seção 5.4 confirmados no card; card de integração com entrada de dados é Alto mesmo numa empresa só (exceções na seção 5.3); automação que só atrasa não é Alto; acesso indevido dentro da mesma empresa é Alto; cobrança que a Zoppy deixa de emitir é Médio pontual e Alto sistêmico; card retroativo herda a severidade do incidente; na dúvida, o nível menor. Cards de origem "interno" não têm cliente relatando: o alcance vem da causa raiz e das evidências do próprio card.
- Seu lote: LOTE (ex.: teste_severidade/pendentes.json, dividido em fatias de até 40 cards). A severidade e a prioridade do board foram removidas de propósito: classifique só pelo conteúdo.

Para CADA card, classifique só com o que está no card. Não invente fato. Cada card pelo próprio mérito. Card duplicado do mesmo incidente que outro card do lote: classifique os dois pelo mérito e registre na pergunta pendente "possível duplicado do #número".

Marque também, em `ponto_em_observacao`, se o card toca um dos pontos em observação da seção 10 do playbook, com uma frase curta; senão null.

Grave em SAIDA um array JSON, um objeto por card, com exatamente:
{"number":int,"eh_bug":bool,"categoria_se_nao_bug":string|null,"nivel":"Baixo|Médio|Alto|Crítico|Catastrófico"|null,"github_severity":"P3|P2|P1|P0|CATASTRÓFICO"|null,"gravidade":"G1|G2|G3"|null,"alcance":"A1|A2"|null,"funcao_parada":bool,"funcao_sempre_alto":"integracao|automacao|cobranca_zoppy|acesso_indevido"|null,"priority_sugerida":"P1"|null,"teste_critico":{"fluxo_inteiro":bool,"sem_contorno":bool,"dinheiro_ou_seguranca":bool},"confianca":"alta|média|baixa","justificativa":"1 a 3 frases, só fatos deste card","pergunta_pendente":string|null,"ponto_em_observacao":string|null,"funcionalidade":"área em poucas palavras"}

Português, sem travessão (nem "—" nem "--"). UTF-8. Confira que o array tem o mesmo número de cards do lote.

Resposta final curta: quantos classificou, distribuição por nível, Críticos e Catastróficos (número e motivo em uma linha), quantos com confiança baixa e quais cards tocaram pontos em observação.
