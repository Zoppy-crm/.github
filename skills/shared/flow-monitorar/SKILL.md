---
name: flow-monitorar
description: >
    Cria monitoramento — alerta ou dashboard — para uma feature, com a documentação nascendo
    junto. Esta skill roda no repo do dev: ela lê o código para descobrir o que a feature já
    emite (identifier de log, métrica, tabela), monta um rascunho e passa o bastão para o
    zoppy-eng-metrics, onde a criação de fato acontece. Use quando o usuário disser "criar
    alerta", "monitorar essa feature", "preciso de um alerta pra isso", "como eu monitoro
    X", "criar dashboard", "quero saber quando isso quebrar", "adicionar observabilidade",
    "alerta de produção", ou logo depois de terminar uma feature quando ele perguntar como
    acompanhar em produção. Também use quando perguntarem qual datasource usar (Loki,
    Prometheus, MySQL, Athena, CloudWatch).
---

# Monitorar uma feature

## Papel

Você está no repo onde a feature foi escrita, e é **só daqui** que dá para saber o que ela
emite. Seu trabalho aqui é levantar esse material e passar o bastão — não é criar o alerta.

A criação acontece no `zoppy-eng-metrics`, e por um motivo concreto: `GRAFANA_URL` e
`GRAFANA_TOKEN` são secrets daquele repo, e é lá que vivem a convenção de alertas, o
critério de datasource, o backtest de limiar e o catálogo. Tentar criar daqui não funciona.

**Não invente o identifier.** Se não achar no código, pergunte. Alerta que consulta um
identifier que ninguém emite nunca dispara e parece saudável na tela — aconteceu 15 vezes
no acervo, e é o modo de falhar mais caro que existe aqui.

## Processo

### 1. Entenda o que tem que ser pego

Uma pergunta por mensagem. Não despeje a lista.

-   **"O que dá errado, e por que isso importa para o cliente?"** — a resposta vira o campo
    mais importante da documentação. Não aceite "a API falha": procure o efeito.
-   **"Quando isso acontecer, o que a pessoa acordada deve fazer?"** — vira o texto que chega
    na notificação. Se a resposta for "olhar o log", pergunte qual log e o que procurar nele.
-   **"Isso já aconteceu? Com que frequência?"** — calibra o limiar depois.

### 2. Ache o que o código já emite

Procure no repo, sem perguntar antes de procurar:

```bash
# identifier de log — o caminho mais comum na Zoppy
grep -rn "identifier:" src/ --include=*.ts | grep -i <termo-da-feature>

# métrica registrada
grep -rn "Counter\|Histogram\|Gauge\|register" src/ --include=*.ts | grep -i <termo>

# a tabela, quando o alerta for sobre estado
grep -rn "@Entity\|repository\." src/ --include=*.ts | grep -i <termo>
```

Anote **o que existe** e **o que não existe**. "O código não emite nada para isso" é uma
resposta legítima e importante: significa que o primeiro passo é instrumentar, não criar
alerta.

Se achar o identifier, registre também os **campos** que ele carrega — eles decidem por
onde a query pode filtrar e agrupar.

### 3. Passe o bastão

Grave o rascunho num arquivo e mande o dev continuar no eng-metrics:

```bash
cat > /tmp/monitorar-<slug>.json <<'JSON'
{
  "repo": "<repo atual>",
  "feature": "<nome curto>",
  "problema": "<o que dá errado e por que importa — resposta da pergunta 1>",
  "acao": "<o que fazer quando acender — resposta da pergunta 2>",
  "emite": {
    "identifier": "<identifier achado, ou null>",
    "campos": ["<campos que o log carrega>"],
    "metrica": "<nome da métrica, ou null>",
    "tabela": "<tabela, ou null>",
    "arquivos": ["<onde você achou>"]
  },
  "frequencia_relatada": "<o que o dev disse na pergunta 3>"
}
JSON
```

E então, literalmente:

```
Levantei o que a feature emite. A criação acontece no eng-metrics, que tem as
credenciais do Grafana e o critério de datasource. Continue com:

    cd ~/source/zoppy-eng-metrics && git pull && \
      claude "/monitorar-alerta /tmp/monitorar-<slug>.json"
```

## O que NÃO fazer aqui

-   **Não escolher o datasource.** O critério é medido e vive no eng-metrics
    (`scripts/datasources.py`). Escolher aqui, de cabeça, é como se chegou a 6 alertas
    `critical` em Athena — uma fonte que conta o passado.
-   **Não sugerir limiar.** Existe backtest lá: ele roda a query sobre os últimos 30 dias e
    diz quantas vezes cada limiar teria acendido. Chutar aqui desperdiça isso.
-   **Não editar JSON de dashboard ou alerta.** O `grafana/` do eng-metrics é **backup**, não
    provisionamento — editar lá não muda produção e o próximo backup sobrescreve.

## Se o dev insistir em criar sem passar pelo eng-metrics

Diga o que se perde, sem impedir: a ficha do catálogo não nasce, o alerta aparece na
listagem marcado como pendente, e o limiar vai sem backtest. Em seguida, ofereça o caminho
completo de novo — ele custa poucos minutos a mais.
