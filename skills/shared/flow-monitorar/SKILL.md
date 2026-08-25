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
    acompanhar em produção. Use também quando um bug acabou de ser classificado como
    `alavanca:monitoramento` pelo `/retorno-solucao` — nesse caso o bug é a especificação. Também use quando perguntarem qual datasource usar (Loki,
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
identifier que ninguém emite nunca dispara e parece saudável na tela — já aconteceu várias
vezes no acervo, e é o modo de falhar mais caro que existe aqui.

## Quando a entrada é um bug já corrigido

Se você chegou aqui porque o `/retorno-solucao` classificou um bug como
`alavanca:monitoramento`, o passo 1 vem quase pronto: **o sintoma já aconteceu de verdade**,
e o card tem a causa raiz escrita. Use o bug como especificação em vez de perguntar do zero —
o que dá errado e por que importa já estão no retorno.

Duas coisas mudam:

-   **O limiar tem um caso real para calibrar.** Diga ao eng-metrics a data da ocorrência: o
    backtest pode rodar sobre a janela em que o bug estava acontecendo, o que é bem melhor que
    calibrar no vazio. Só funciona se a fonte tiver memória daquele período — se não tiver,
    diga isso em vez de fingir que o limiar foi provado.
-   **Se o sinal não existe, ele sobe no PR do bugfix** — não num card para depois. O dev está
    no código e acabou de entender a causa; é o momento mais barato que existe para emitir o
    log ou a métrica que faltava. Sem o sinal, não há alerta possível, e o card de alerta
    nasceria morto esperando instrumentação.

Isso vale **só** quando a alavanca é monitoramento. Em bug de regra de negócio o caminho é
teste, não alerta — alerta avisa depois que o bug aconteceu, e não derruba reincidência.

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

E então, literalmente — trocando a skill conforme o que ele quer:

```
Levantei o que a feature emite. A criação acontece no eng-metrics, que tem as
credenciais do Grafana e o critério de datasource. Continue com:

    cd ~/source/zoppy-eng-metrics && git checkout master && git pull && \
      claude "/monitorar-alerta /tmp/monitorar-<slug>.json"
```

**O `master` atualizado não é detalhe de higiene.** Tudo que a skill de lá vai ler muda
toda semana: o critério de datasource, o catálogo de sinais que diz o que o código emite, a
convenção, as fichas. Num clone velho ela recomenda com o mundo de duas semanas atrás e não
tem como saber disso — e é uma recomendação errada que parece certa, que é o pior tipo.

Se ele não tiver o repo, é um clone e pronto:

```bash
git clone git@github.com:Zoppy-crm/zoppy-eng-metrics.git ~/source/zoppy-eng-metrics
```

**Alerta ou dashboard são skills diferentes lá**, porque as decisões são diferentes:

| Ele quer                   | Passe para             | Porque muda                                         |
| -------------------------- | ---------------------- | --------------------------------------------------- |
| ser avisado quando quebrar | `/monitorar-alerta`    | tem limiar, backtest e teto de severidade por fonte |
| uma tela para acompanhar   | `/monitorar-dashboard` | tem layout, tipo de gráfico e descrição por painel  |

Na dúvida, a pergunta que separa é: **"alguém precisa ser acordado por isso?"** Se sim, é
alerta. Se a resposta for "não, mas eu quero olhar de vez em quando", é dashboard — e
insistir em alerta cria mais um que o time aprende a ignorar.

As duas coisas juntas são comuns e a ordem é essa: o dashboard mostra o comportamento, e é
olhando para ele que se escolhe o limiar do alerta com dado em vez de no olho.

## O que NÃO fazer aqui

-   **Não escolher o datasource.** O critério é medido e vive no eng-metrics
    (`scripts/datasources.py`). Escolher aqui, de cabeça, é como se chegou a alerta
    `critical` em Athena — uma fonte que conta o passado.
-   **Não sugerir limiar.** Existe backtest lá: ele roda a query sobre os últimos 30 dias e
    diz quantas vezes cada limiar teria acendido. Chutar aqui desperdiça isso.
-   **Não editar JSON de dashboard ou alerta.** O `grafana/` do eng-metrics é **backup**, não
    provisionamento — editar lá não muda produção e o próximo backup sobrescreve.
-   **Não gerar JSON de dashboard para o dev colar na UI.** Era o que a skill antiga fazia, e
    é a origem do passivo: o dashboard nasce fora do catálogo, sem ficha e sem descrição nos
    painéis. Desfazer isso custou um mutirão de semanas.

## Se o dev insistir em criar sem passar pelo eng-metrics

Diga o que se perde, sem impedir: a ficha do catálogo não nasce, o alerta aparece na
listagem marcado como pendente, e o limiar vai sem backtest. Em seguida, ofereça o caminho
completo de novo — ele custa poucos minutos a mais.

O que **não** fazer é tentar suprir daqui. Você não tem as credenciais, não tem o critério e
não tem o catálogo; o que sairia daqui seria um palpite com cara de recomendação.
