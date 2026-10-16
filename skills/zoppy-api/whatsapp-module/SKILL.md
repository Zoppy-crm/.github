---
name: whatsapp-module
description: >
    Como construir e migrar código para o módulo WhatsApp do zoppy-api (src/modules/whatsapp e
    src/platform): submódulos accounts, templates, contacts e messaging, cada um com as camadas
    api, access, application, domain (model, values, ports), repository e infrastructure; o
    contrato público; eventos no EventBridge; filas whatsapp.*; erros por categoria; logs e config;
    e o roteiro de cinco passos para tirar uma capacidade do legado sem quebrar produção. Use
    sempre que tocar em src/modules/whatsapp/**, src/platform/**, em código legado de WhatsApp que
    está sendo migrado (Wpp*, whatsapp-*, wpp-*), quando uma mensagem do lint citar esta skill, ou
    quando pedirem: "migrar para o módulo whatsapp", "submódulo", "fachada", "api do submódulo",
    "caracterização", "drenar fila", "evento do whatsapp", "assinar evento", "lista de exceções".
---

# Módulo WhatsApp

O módulo é um monolito modular dentro do zoppy-api, a um passo de virar serviço próprio. O CRM, o
wpp-commerce e produtos futuros consomem o canal **só** pelo contrato público e pelos eventos. Esta
skill vale apenas para esse módulo e para o `src/platform/`; o resto do repositório segue as
convenções de sempre.

## Mapa

```
src/platform/                 portas reutilizáveis: context, logging, queue, events, inbound
src/modules/whatsapp/
├── public/                   o que o resto do app enxerga: fachadas, Commands, tokens, eventos, erros públicos
├── whatsapp.module.ts        exporta só tokens de public/
├── accounts/                 conta, telefone, gerente, saúde e alertas
├── templates/                templates da Meta e variáveis
├── contacts/                 identidade, consentimento e janela de 24h
└── messaging/                envio, status, recebimento
    ├── api/                  contrato entre submódulos: interface, tipos de leitura, token
    ├── access/               fachada e api implementadas, controllers, processors, mappers Command → Input
    ├── application/          MessagingApplication e os Inputs
    ├── domain/
    │   ├── model/            agregados e entidades
    │   ├── values/           objetos de valor e erros do domínio
    │   └── ports/            interfaces que o lado de fora implementa
    ├── repository/           SequelizeMessageRepository e o mapper
    ├── infrastructure/       adaptadores: Meta, fila, etc.
    ├── messaging.config.ts
    ├── messaging.logs.ts
    ├── messaging.queues.ts
    └── messaging.module.ts
```

## Onde ler cada assunto

| Preciso de | Leia |
|---|---|
| O que cada camada faz, pode importar e não pode | [references/camadas.md](references/camadas.md) |
| Esqueleto de fachada, api, application, agregado, porta, repositório, processor, evento | [references/receitas.md](references/receitas.md) |
| Tirar uma capacidade do legado (os cinco passos) | [references/migrar.md](references/migrar.md) |
| Código novo convivendo com legado | [references/coexistencia.md](references/coexistencia.md) |
| Filas, drenagem, eventos e assinatura | [references/filas-e-eventos.md](references/filas-e-eventos.md) |
| Erros, logs, config e contexto do tenant | [references/erros-logs-config.md](references/erros-logs-config.md) |
| Uma mensagem do lint (L1 a L23) | [references/lint.md](references/lint.md) |

## As regras que não se negociam

1. **De fora do módulo, só `whatsapp/public`.** Ninguém importa `application/`, `domain/` ou `repository/` de um submódulo.
2. **Entre submódulos, só o `api/` do irmão**, e só a partir da `application` (o `<sub>.module.ts` importa o módulo irmão para a injeção). O `api/` devolve tipos de leitura, nunca agregados, e expõe operações com nome de negócio (`deactivate`, `block`), nunca CRUD (`update`, `save`).
3. **Models `Wpp*` só no `repository/` do submódulo dono da tabela.**
4. **O domain não conhece framework**: sem Nest, Sequelize, logger, config. Só o núcleo de `@Zoppy-crm/exceptions`.
5. **Migrar é passar a ser o único que grava.** Uma milestone só fecha quando nenhum código legado grava nas tabelas que ela assumiu.
6. **Schema só aditivo.** Nada de renomear ou apagar coluna; o legado tem que entender o que o código novo grava.
7. **Comportamento preservado.** Bug encontrado vira card na hora, sub-issue do epic, com o teste que o prova ([migrar.md › Bug encontrado na migração](references/migrar.md)); a migração não corrige no caminho. A única mudança intencional do épico é a mensagem nascer no envio.
8. **Sem `// eslint-disable` e sem comentários no código.** Exceção de lint só por arquivo, na config, com motivo.

## Antes de abrir o PR

- [ ] `npm run lint` e `npm run lint:whatsapp` sem erro
- [ ] Specs dos arquivos alterados verdes (`npm run test -- --testPathPatterns="<caminho>"`)
- [ ] PR entre 200 e 400 linhas, uma mudança só
- [ ] Se trocou um chamador: o trecho legado sem uso foi apagado no mesmo PR
- [ ] Se um arquivo deixou de violar L1 ou L6: saiu da lista de exceções no mesmo PR
- [ ] Bugs achados neste PR têm card aberto e aparecem na descrição, em "bugs preservados"
- [ ] Nenhum `@InjectQueue`, `Scope.REQUEST`, `process.env` fora de `*.config.ts`, `console.*`
