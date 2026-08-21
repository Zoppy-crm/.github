---
name: monitorar-alerta
description: >
    Cria um alerta no Grafana com a documentação nascendo junto — recomenda o datasource
    com base no critério medido do repo, escolhe o limiar por backtest sobre os últimos 30
    dias, cria a regra e grava a ficha do catálogo no mesmo passo. Roda no zoppy-eng-metrics,
    que é onde vivem as credenciais do Grafana, a convenção e o catálogo. Use quando o
    usuário chegar com um rascunho de /tmp/monitorar-*.json vindo da skill flow-monitorar,
    quando disser "criar alerta", "monitorar isso", "qual datasource usar", "escolher
    limiar", "backtest de alerta", ou quando quiser documentar um alerta existente.
---

# Criar alerta com a ficha junto

## Papel

Você é quem impede que nasça mais um alerta que não avisa ninguém. O acervo tem 190, e as
falhas que custaram caro foram sempre silenciosas: alerta que nunca acende, alerta que
acende no vazio, alerta que conta o passado, alerta sem instrução para quem foi acordado.

Nada aqui é opinião sua. **Leia os fatos do repo em vez de lembrar deles** — eles mudam, e
uma skill que repete número envelhece calada:

| O que                                                 | Onde ler                             |
| ----------------------------------------------------- | ------------------------------------ |
| Critério de datasource, teto de severidade, intervalo | `scripts/datasources.py`             |
| O que o código do zoppy-api emite                     | `docs/alertas/sinais-zoppy-api.json` |
| O que a convenção obriga                              | `docs/convencao-de-alertas.md`       |
| O que se escreve na ficha, e o que não                | `docs/formato-da-ficha.md`           |

Comece **lendo `scripts/datasources.py`**. Ele tem a árvore de decisão (`DECISAO`), a
pergunta que separa Loki de Prometheus (`DISCRIMINANTE`), a regra de cardinalidade
(`REGRA_DURA`) e o perfil de cada fonte. É a fonte única.

## Processo

### 1. Recupere o contexto

Se veio um rascunho de `/tmp/monitorar-*.json`, leia. Ele traz o problema, a ação e o que o
código emite — levantado no repo da feature, que é o único lugar onde isso se sabe.

Sem rascunho, faça as perguntas você mesmo, uma por mensagem: o que dá errado e por que
importa; o que a pessoa acordada deve fazer; com que frequência já aconteceu.

### 2. Escolha o datasource percorrendo a árvore

Percorra `DECISAO` em ordem. Volume decide qual fonte **consegue** responder; latência
decide só até onde a severidade pode ir.

Antes de recomendar Loki, **confirme o identifier no catálogo de sinais**:

```bash
python3 -c "
import json
s={x['identifier']:x for x in json.load(open('docs/alertas/sinais-zoppy-api.json'))['sinais']}
x=s.get('IDENTIFIER_AQUI')
print(json.dumps(x, ensure_ascii=False, indent=1) if x else 'NAO ESTA NO CATALOGO')"
```

Três resultados possíveis, e três respostas diferentes:

-   **Está no catálogo** → Loki é viável. Os `campos` e `eventos` dizem por onde a query pode
    filtrar e agrupar. Os `levels` dizem se faz sentido tratar como erro.
-   **Não está, e o repo é o zoppy-api** → _provavelmente_ o código não emite. Mas o catálogo
    declara 568 chamadas sem identifier e 130 expressões não resolvidas, então **não afirme**:
    diga que não conseguiu confirmar e peça para o dev checar. Falso positivo é o pior
    resultado.
-   **O repo não é o zoppy-api** → não há catálogo. Pergunte, não adivinhe.

Ao recomendar, diga **por que** e o que a fonte custa — os campos `quando`, `quando_nao` e
`custo` do perfil existem para isso.

### 3. Escolha o limiar por backtest, não no olho

Nunca sugira um número sem medir. Monte 3 ou 4 candidatos e rode todos de uma vez:

```bash
gh workflow run backtest-alerta.yml \
  -f ds=<uid> -f expr='<query>' -f limiares='1 5 10 25' \
  -f op=gt -f duracao=10m -f dias=30
```

Espere e leia o resultado. A tabela dá disparos, disparos/dia e fração do tempo aceso.
Como ler:

-   **0 disparo em 30 dias** → o alerta nunca acende. São 15 assim no acervo.
-   **~1 por semana** → é o que se espera de algo que vale acordar alguém.
-   **vários por dia** → o time aprende a ignorar, e ignora também quando importar.
-   **aceso mais de 50% do tempo** → não é alerta, é estado. Vira dashboard.

Se a query voltar vazia, isso é resultado, não erro: ou o sinal não existe, ou não houve
ocorrência. Pare e confirme antes de seguir.

O backtest recusa query com `$reduce`/`$math` — nesses casos monte na UI e confira o limiar
lá, porque a conta daria errada em silêncio.

### 4. Escreva a ficha **com** o dev, no mesmo diálogo

Não é etapa separada, e não é formulário. São as três coisas que o Grafana não tem como
saber, e que já foram respondidas nas perguntas do passo 1:

-   **`ficha.o`** — que sintoma real isso pega, e por que importa para o negócio. Não é a
    query em prosa. É o texto que faz alguém entender o risco sem conhecer o sistema.
-   **`ficha.d`** — como o número sai: agregação, limiar, por quanto tempo sustentado. É o que
    permite discutir se o limiar é o certo.
-   **`ficha.n`** — a ressalva: o que o alerta _não_ mede. Opcional, mas 155 das 187 fichas
    têm uma.

E o que vai no Grafana, não na ficha:

-   **`annotations.description`** — o que fazer. **Chega na notificação**, e é o único texto
    que quem foi acordado lê antes de abrir qualquer coisa. Faltava em 68 dos 190.

Leia `docs/formato-da-ficha.md` se tiver dúvida sobre o que vai onde. Tem um exemplo de par
bem escrito lá.

### 5. Crie

O intervalo de avaliação **não se escolhe** — sai do critério. Monte o spec (veja o formato
com `python3 scripts/cria_alerta.py --exemplo`), simule primeiro:

```bash
gh workflow run cria-alerta.yml -f spec="$(cat spec.json | tr -d '\n')" -f aplicar=false
```

O script **recusa** enquanto faltar ficha, instrução ou severidade que caiba na fonte. Se
recusar, a mensagem diz o próximo passo — resolva e rode de novo. Não contorne.

Aplicando, ele cria a regra e grava a ficha em `docs/alertas/resumos-alertas.json`.

### 6. Feche

```bash
python3 docs/alertas/_build.py        # o catálogo tem que gerar
python3 docs/alertas/_valida.py       # 0 erros
python3 -m unittest discover -s tests
```

Abra o PR com a ficha. O deploy do catálogo é automático no merge.

## Alerta que espera código não publicado

Se a feature ainda não subiu, o alerta vai nascer sem sinal para consultar — e apareceria
como defeito. Existe rótulo para isso: `aguardando-deploy`. Crie pausado, marque, e o
catálogo tira da fila. Quando o sinal voltar a ser emitido, ele avisa sozinho que dá para
religar. Ver `scripts/aguardando_deploy.py`.

## Erros que este repo já pagou, e que você não deve repetir

-   **Não escolha o datasource de cabeça.** Athena não sustenta `critical`: o dado chega ao
    lake com atraso, então o alerta conta o passado. Baixar o `for` não resolve. São 6 assim.
-   **Não aperte o intervalo "para detectar mais rápido".** Detecção é `for` + intervalo, e o
    ganho encolhe rápido enquanto o custo cresce linear. Foi assim que 92 dos 190 alertas
    foram parar em 1 minuto.
-   **Não ponha `companyId` como label de Prometheus.** Cardinalidade alta derruba o servidor.
-   **Não edite JSON em `grafana/`.** É backup, não provisionamento. O próximo backup
    sobrescreve.
-   **Não escreva a ficha depois.** É o que gerou o mutirão de semanas que criou este
    catálogo. No mesmo diálogo custa minutos.
