---
name: flow-feature-docs
description: >-
    Executa um subagent dedicado para verificar e atualizar a documentação interna (OKF Knowledge Bundle) e gerar/atualizar rascunhos de artigos da Central de Ajuda (Help Center) antes de abrir ou atualizar um Pull Request apontando para branches de release (master, main, staging, mirror). Use esta skill sempre que abrir um PR para master, main, staging ou mirror, ou quando o usuário pedir para "documentar a feature", "checar documentação da feature", "atualizar docs para o PR", "gerar rascunho da central de ajuda" ou "/flow-feature-docs".
---

# Feature Documentation & Help Center Subagent (`flow-feature-docs`)

Toda mudança que vai para `master`, `main`, `staging` ou `mirror` (especialmente em `zoppy-api`, `zoppy-FE`, `zoppy-admin-fe`, `zoppy-whatsapp-commerce`, `zoppy-workflow` e demais repositórios com branches de espelhamento/homologação) deve passar por um **subagent de documentação** antes de abrir ou atualizar o Pull Request.

O objetivo é duplo:

1. **Memória técnica do repositório (OKF Knowledge Bundle):** garantir que regras de negócio, invariantes e o *porquê* das decisões fiquem registrados em `overview.md`, concepts e `log.md` no próprio repositório.
2. **Documentação de produto revisada por humanos (Central de Ajuda):** se a mudança cria ou altera tela, fluxo, regra visível ao lojista, limite, integração ou mensagem de erro, gerar ou atualizar um **rascunho (`status: 'rascunho'`)** para a Central de Ajuda (`ajuda.zoppy.com.br`) — gerenciada e publicada com revisão humana no **Zoppy Admin (`zoppy-admin-fe` → `/dashboard/help-center`)**.

> **Regra de ouro:** nenhum artigo da Central de Ajuda vai direto como `publicado` por automação de PR. Todo conteúdo criado ou editado pelo subagent nasce como **rascunho (`rascunho`)** (ou `draftData` pendente de revisão em artigo existente) para aprovação e publicação humana no Admin.

---

## Como executar (Delegação Obrigatória para Subagent)

**Sempre execute este fluxo dentro de um subagent dedicado** (`Task` / `invoke_subagent`) para não poluir o contexto principal com a leitura do diff completo e dos arquivos de documentação.

Passe ao subagent:

- A branch base do PR (`<base-branch>`, ex.: `master`, `staging`, `mirror`, `main`)
- O resumo dos commits da branch atual
- As instruções completas abaixo

---

## Procedimento do Subagent

### Passo 1: Inspecionar o Diff da Branch

Obtenha a lista de arquivos alterados e o diff contra a branch base:

```bash
git diff --name-status origin/<base-branch>...HEAD
git diff origin/<base-branch>...HEAD
```

Classifique o impacto da mudança em duas dimensões:

1. **Impacto Interno (OKF Knowledge Bundle):**
   - Mudou regra de negócio, cálculo, máquina de estados, permissão, contrato entre módulos, fila, integração ou decisão arquitetural?
2. **Impacto Externo / Lojista (Central de Ajuda):**
   - Adicionou ou alterou funcionalidade visível ao usuário/lojista (nova tela, botão, configuração, fluxo de campanha/automação/cupom/WhatsApp, integração de e-commerce/ERP, limite operacional ou sintoma de erro recorrente)?

---

### Passo 2: Verificar e Atualizar o OKF Knowledge Bundle (Interno)

Se o repositório possuir `/index.md` e/ou `/references/okf-authoring.md`:

1. Leia `/index.md` para localizar a área/feature correspondente aos arquivos tocados no diff.
2. Leia `/references/okf-authoring.md` antes de criar ou editar qualquer arquivo `.md` do bundle.
3. Verifique o `overview.md` e os concepts da feature tocada:
   - **Se algum concept divergiu do código novo ou ficou incompleto:** atualize o arquivo no mesmo passo (documentando propósito, regras de negócio e o *porquê* — nunca duplicando assinatura de código).
   - **Se a feature ainda não tinha entrada na área documentada e introduz regras de negócio relevantes:** crie ou amplie o concept correspondente e aponte em `index.md`.
4. **Registro no `log.md`:** se houve mudança estrutural, trade-off técnico ou alteração de regra de negócio numa área que possui `log.md`, adicione uma entrada no topo (`YYYY-MM-DD`, mais recente primeiro) explicando a **decisão e a motivação**.
5. Se foram editados arquivos `.md` do OKF, faça commit na branch atual (`docs: update OKF documentation for <feature>`).

---

### Passo 3: Verificar e Gerar Rascunho da Central de Ajuda (`ajuda.zoppy.com.br`)

Avalie se a mudança afeta o uso do produto pelo lojista, operação ou suporte.

#### 3.1 Quando NÃO gerar artigo da Central de Ajuda

- Refatoração puramente interna sem mudança de comportamento visível
- Ajustes de infraestrutura, CI/CD, observabilidade ou testes internos
- Correção de bug silencioso que apenas restaura o comportamento já documentado

Se não houver impacto na Central de Ajuda, registre explicitamente a justificativa no relatório final (ex.: `"Sem impacto na Central de Ajuda: alteração restrita a índice de banco e telemetria interna"`).

#### 3.2 Quando GERAR ou ATUALIZAR rascunho da Central de Ajuda

Se o PR cria uma feature nova ou altera um fluxo visível ao lojista:

1. Escolha o **tipo de artigo (`type`)** adequado:
   - `tutorial`: passo a passo com começo, meio e fim (`steps`, `before`, `check`, `faq`)
   - `guia`: explicação conceitual, regras e tabelas comparativas (`sections`)
   - `resposta`: pergunta direta com resposta curta nos primeiros 300 caracteres (`answer`, `details`)
   - `problema`: diagnóstico de erro ou sintoma (`symptomGroup`, `causes`, `expected`, `checks`, `escalateWith`)
   - `glossario`: definição curta de métrica ou termo do CRM (`definition`, `example`)
2. Escolha o **assunto (`topic`)** entre os 12 assuntos canônicos (ou `glossario`):
   - `primeiros-passos`, `integracoes`, `clientes-e-segmentos`, `campanhas-e-whatsapp`, `automacoes`, `cupons-e-cashback`, `indicou-ganhou`, `vendas-no-whatsapp`, `relatorios-e-metricas`, `configuracoes-e-conta`, `problemas-comuns`, `glossario`
3. Monte o payload do rascunho seguindo as regras editoriais da Central de Ajuda:
   - **`status`**: SEMPRE `'rascunho'`
   - **Texto inline**: use apenas `**negrito**`, `` `código` `` e `[texto](/artigo/slug)` (sem tags HTML, sem emojis, sem `"clique aqui"`, sem jargão interno de código como nomes de tabelas ou filas)
   - **`summary`**: 1 a 2 frases claras em português (15 a 320 caracteres)
4. **Envie ou registre o rascunho para revisão humana no Admin (`zoppy-admin-fe`):**
   - Se a API da Zoppy estiver acessível com token (`ZOPPY_API_URL` + `ZOPPY_ADMIN_TOKEN`), salve o rascunho via endpoint `POST /api/help-center/articles/draft` (que cria um artigo em `rascunho` ou grava `draftData` num artigo publicado sem alterar o site no ar).
   - Caso não haja credencial de API configurada no ambiente local da execução, inclua o JSON estruturado do rascunho (ou o comando/payload pronto para importação no `/dashboard/help-center` do `zoppy-admin-fe`) na seção `## Documentação` do PR para que o revisor aprove e publique na tela **Central de Ajuda** do Admin.

#### Formato do Payload de Rascunho (`POST /api/help-center/articles/draft`)

```json
{
    "slug": "nome-do-artigo-em-kebab-case",
    "topic": "configuracoes-e-conta",
    "type": "tutorial",
    "status": "rascunho",
    "title": "Como configurar [nome da funcionalidade]",
    "summary": "Aprenda a ativar e configurar [funcionalidade] na sua conta Zoppy e valide o funcionamento.",
    "owner": "produto",
    "reviewedAt": "YYYY-MM-DD",
    "hubSection": "Configurações gerais",
    "platforms": ["todas"],
    "synonyms": ["termo alternativo 1", "termo alternativo 2"],
    "related": [],
    "todo": ["Validar prints/nomes finais dos botões no Admin antes de publicar"],
    "before": ["Ter perfil Administrador na conta Zoppy."],
    "steps": [
        {
            "title": "Acesse a tela da funcionalidade",
            "body": [
                "No menu lateral da Zoppy, clique em **Configurações**.",
                {
                    "type": "note",
                    "tone": "info",
                    "title": "Dica",
                    "body": "As alterações ficam salvas como rascunho até você publicar."
                }
            ]
        }
    ],
    "check": ["Confirme que o status aparece como ativo na listagem."],
    "faq": []
}
```

---

### Passo 4: Retornar a Seção `## Documentação` para o PR Body

O subagent deve devolver ao agente principal o bloco markdown pronto para ser incluído na descrição do Pull Request:

```markdown
## Documentação

- **OKF Knowledge Bundle:** [Atualizado em `caminho/overview.md` e `log.md` | Sem alterações necessárias (motivo)]
- **Central de Ajuda (`ajuda.zoppy.com.br`):** [Rascunho criado/atualizado: `<topic>/<slug>` (`status: rascunho`) para revisão e publicação no Zoppy Admin (`/dashboard/help-center`) | Sem impacto para o lojista (motivo)]
```

Se um rascunho da Central de Ajuda foi gerado localmente sem envio direto à API, anexe-o dentro de um bloco `<details><summary>📄 Rascunho sugerido para a Central de Ajuda (revisar no Admin)</summary>...</details>` logo abaixo da seção `## Documentação`.
