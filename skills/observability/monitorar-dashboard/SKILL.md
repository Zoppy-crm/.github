---
name: monitorar-dashboard
description: >
    Cria um dashboard no Grafana com a documentação nascendo junto — escolhe a fonte pelo
    critério medido do repo, copia a forma de um dashboard real do acervo em vez de inventar
    JSON, e grava a ficha do catálogo no mesmo passo. Roda no zoppy-eng-metrics, que é onde
    vivem as credenciais do Grafana, o critério e o catálogo. Use quando o usuário chegar com
    um rascunho de /tmp/monitorar-*.json vindo da skill flow-monitorar, quando disser "criar
    dashboard", "montar um painel", "quero acompanhar isso numa tela", "qual gráfico usar",
    ou quando quiser documentar um dashboard que já existe.
---

# Criar dashboard com a documentação junto

## Papel

Você é quem impede que nasça mais um painel que ninguém sabe o que mede.

**Todo dashboard é documentado, e a documentação nasce com ele.** Não é meta nem boa
intenção: é o que o gate cobra, e é a razão de esta skill existir. Escrever depois já custou
um mutirão de semanas neste repo. Escrever junto custa a mesma conversa que já se tem ao
escolher o gráfico.

Nada aqui é opinião sua. **Leia os fatos do repo em vez de lembrar deles** — eles mudam, e
uma skill que repete número envelhece calada:

| O que                                          | Onde ler                                |
| ---------------------------------------------- | --------------------------------------- |
| Critério de datasource: volume, frescor, custo | `scripts/datasources.py`                |
| O que o código do zoppy-api emite              | `docs/alertas/sinais-zoppy-api.json`    |
| O que se escreve na ficha, e o que não         | `docs/formato-da-ficha.md`              |
| A definition of done de dashboard              | `docs/boas-praticas-observabilidade.md` |
| **Dashboards reais, para copiar a forma**      | `grafana/dashboards/`                   |

## Não invente JSON de dashboard

Esta é a diferença que mais economiza tempo, e a que mais evita erro.

O acervo está cheio de dashboards que funcionam, com o `schemaVersion` certo, o
`pluginVersion` certo e as variáveis que este Grafana tem. **Copie a forma de um que já se
pareça com o que você quer** em vez de montar do zero:

```bash
# um que use a mesma fonte e o mesmo tipo de painel
grep -rl '"type": "stat"' grafana/dashboards/features/ | head -5

# a forma inteira de um deles, sem os dados
python3 docs/alertas/_digest.py grafana/dashboards/<caminho>.json
```

Um skeleton escrito dentro de uma skill envelhece: a versão do Grafana sobe, o uid da fonte
muda, a variável some. Um dashboard do acervo é do backup de hoje.

## Processo

### 0. Confirme que está lendo o repo de hoje

Antes de ler qualquer coisa:

```bash
git -C . rev-parse --abbrev-ref HEAD && git -C . fetch -q && git -C . status -sb | head -1
```

Se não estiver em `master` sincronizado, pare e atualize. Tudo que esta skill manda ler
muda toda semana — o critério de datasource, o catálogo de sinais, a convenção, as fichas.
Num clone atrasado ela recomenda com o mundo de duas semanas atrás **e não tem como saber
disso**: sai uma recomendação errada com cara de certa, que é o pior tipo.

Se o diretório atual não for o `zoppy-eng-metrics`, esta skill não roda aqui. Peça para o
dev abrir o terminal lá — é onde as credenciais do Grafana e o catálogo existem.

### 1. Recupere o contexto

Se veio um rascunho de `/tmp/monitorar-*.json`, leia — ele traz o problema e o que o código
emite, levantado no repo da feature, que é o único lugar onde isso se sabe.

Sem rascunho, pergunte você mesmo. **Uma pergunta por mensagem**, não despeje a lista:

-   **"Que decisão essa tela deve permitir tomar?"** — é a pergunta que separa dashboard útil
    de coleção de números. A resposta vira `ficha.o`. Se for "acompanhar", insista: acompanhar
    para decidir o quê?
-   **"Quem vai olhar, e quando?"** — plantão às 3h e revisão de semana pedem telas diferentes.
-   **"O que é normal?"** — sem isso não há como escrever a descrição de painel nenhum, e é a
    informação que só o dev tem.

### 2. Escolha a fonte percorrendo o critério

Leia `scripts/datasources.py` e percorra `DECISAO` em ordem. Volume decide qual fonte
**consegue** responder; frescor decide se a tela mostra agora ou ontem.

Num dashboard o teto de severidade não se aplica — ninguém é acordado por um painel. Mas o
frescor se aplica em dobro: **uma tela que parece ao vivo e mostra o lake de ontem é pior
que uma tela que declara o atraso.** Se a fonte tem latência, diga isso na `description` do
painel.

Antes de usar Loki, confirme o identifier no catálogo de sinais:

```bash
python3 -c "
import json
s={x['identifier']:x for x in json.load(open('docs/alertas/sinais-zoppy-api.json'))['sinais']}
x=s.get('IDENTIFIER_AQUI')
print(json.dumps(x, ensure_ascii=False, indent=1) if x else 'NAO ESTA NO CATALOGO')"
```

Não está no catálogo não prova que o código não emite — a análise estática declara o que não
alcançou. Diga que não conseguiu confirmar e peça para o dev checar. Falso positivo é o pior
resultado.

### 3. Proponha o layout antes de escrever qualquer JSON

Diga que gráfico para cada coisa e **por quê**. Espere o aceite. O tipo certo depende da
decisão que a tela sustenta, não do dado:

| Se a pessoa precisa                | Painel                    |
| ---------------------------------- | ------------------------- |
| saber se está dentro ou fora agora | `stat`, cor por threshold |
| ver se está piorando               | `timeseries`              |
| achar qual dos N está pior         | `bar chart` ou `table`    |
| entender por que um número mudou   | `logs`, no fim da tela    |

Duas coisas que o acervo aprendeu na prática:

-   **Termine com uma seção de logs.** Quando um contador fica estranho, é para lá que se vai.
-   **`graphMode: "none"` em stat de contador.** `"area"` só faz sentido com série temporal, e
    um sparkline embaixo de um total acumulado sugere tendência que não existe.

### 4. Escreva as descrições **no mesmo diálogo**

Não é etapa separada e não é formulário. São duas coisas diferentes, e escrever a mesma
frase nas duas desperdiça a segunda:

-   **`description`, no painel do Grafana** — _o que_ mede, e o que fazer com o número.
    Aparece na tela, para quem está olhando às 3h da manhã. Em painel de título óbvio,
    reafirmar o título é ruído: `2xx` contando 2xx não precisa de "conta os 2xx", precisa de
    **o que é normal, o que é sinal de problema, e qual a leitura errada tentadora**.
    Markdown, não HTML.
-   **linha de `ficha.pn`** — _como_ calcula. `[id, título, fonte, a conta]`. Aparece no
    catálogo, para quem precisa decidir se confia no número. HTML inline permitido.

Mais `ficha.o` (que pergunta a tela responde), `ficha.c` (a composição) e `ficha.q` (de onde
vem o dado).

**A chave é o `id` do painel, nunca o título.** Muito painel do acervo repete título, e
casar por ele já soltou a ficha de centenas deles em silêncio, num renome que ninguém viu.

### 5. Crie

Veja o formato com `python3 scripts/cria_dashboard.py --exemplo`. Simule primeiro:

```bash
gh workflow run cria-dashboard.yml -f spec="$(cat spec.json | tr -d '\n')" -f aplicar=false
```

O script **recusa** enquanto faltar `description`, `id`, ou a linha de ficha nos painéis
compostos. Se recusar, a mensagem diz o próximo passo — resolva e rode de novo. **Não
contorne indo criar na UI**: é exatamente o caminho que produziu o passivo.

Aplicando, ele cria o dashboard, grava a ficha e abre o PR com ela.

### 6. Feche

```bash
python3 docs/alertas/_build.py         # o catálogo tem que gerar
python3 docs/alertas/_valida.py        # 0 erros
python3 -m unittest discover -s tests
```

O deploy do catálogo é automático no merge.

## O painel composto é onde o número mente

O gate exige a linha de ficha só em painel **composto** — mais de uma consulta,
transformation, unidade percentual, ou divisão na query. Não é burocracia seletiva: é onde
o erro é invisível.

O caso que originou a regra: um painel de CTR mostrou por meses um número um terço maior
que o real, porque o numerador contava cliques de todos os formatos e o denominador só
impressões de vídeo. Nenhuma das duas consultas estava errada. A combinação estava, e
nenhuma descrição pegaria isso, porque descrição fala da intenção. A conta escrita pega.

Quando montar um painel de razão, escreva na ficha **o numerador e o denominador**, não
"taxa de clique".

## Erros que este repo já pagou

-   **Não gere JSON para o dev colar na UI.** É o que a skill antiga fazia, e é a origem do
    passivo: o dashboard nasce fora do catálogo, sem ficha, e ninguém percebe até alguém
    precisar dele.
-   **Não edite JSON em `grafana/`.** É backup, não provisionamento — editar ali não muda
    produção e o próximo backup das 6h sobrescreve.
-   **Não deixe painel sem `id`.** Sem ele não há deep link: nem do catálogo, nem do
    `__panelId__` de um alerta. Conserta-se no Grafana com `scripts/grafana_panel_ids.py`,
    **não** adaptando a ficha para casar por título.
-   **Não aceite "Panel Title" nem "New dashboard".** O acervo tem painel e dashboard assim,
    e ninguém sabe o que são.
-   **Não classifique dashboard por nome.** Já errou nos dois sentidos aqui: dashboards com
    "Teste" no título eram produção.
