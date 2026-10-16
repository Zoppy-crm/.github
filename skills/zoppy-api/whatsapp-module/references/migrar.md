# Migrar uma capacidade: os cinco passos

Toda milestone, do F1 ao F5, segue estes passos nesta ordem. Exemplo usado: bloquear um contato
(F3), que hoje o `client-block.service` grava direto em `WppContacts.isBlocked`.

## 1. Mapear e caracterizar

**Objetivo:** saber o que muda e congelar o comportamento atual antes de mexer.

### Inventário

Salvo no card da milestone, com caminho de arquivo:

- **Quem grava** nas tabelas que o submódulo vai assumir (model, domain legado, SQL). Vira a lista de trocas do passo 3.
- **Quem só lê.** Vira entrada na lista de exceções do lint.
- **Filas, crons e endpoints** da capacidade. Dizem se haverá drenagem no passo 4.

### Testes de caracterização

Uma suíte por capacidade, em `src/modules/whatsapp/<sub>/characterization/`. Os cenários são
escritos uma vez e executados por um **driver**: um adaptador fino que diz ao teste como executar
a ação. Assim o mesmo teste roda contra o legado e contra o módulo, e qualquer diferença entre os
dois aparece como uma linha vermelha.

```ts
interface BlockContactDriver {
    readonly name: string;
    block(input: { tenantId: string; phone: string }): Promise<void>;
}

const legacyBlockDriver: BlockContactDriver = {
    name: 'legado',
    block: ({ tenantId, phone }) => clientBlockService.blockPhones(tenantId, [phone]),
};

const contactsApiDriver: BlockContactDriver = {
    name: 'módulo',
    block: ({ tenantId, phone }) => contactsApi.block(tenantId, phone),
};

const drivers: BlockContactDriver[] = [legacyBlockDriver];

describe.each(drivers)('bloquear contato ($name)', (driver) => {
    it('bloqueia todas as variantes do telefone', async () => {
        await seedContacts(tenantId, ['+5511999990000', '11999990000']);
        await driver.block({ tenantId, phone: '+5511999990000' });
        expect(await findBlockedPhones(tenantId)).toEqual(['+5511999990000', '11999990000']);
    });
});
```

- **Afirme só efeito observável:** linhas no banco depois da ação (SQLite em memória do `TestUtils`), chamadas nos mocks de fronteira (SDK da Meta, AWS), jobs e eventos publicados, erro devolvido. Nunca qual método interno foi chamado: é isso que permite rodar o mesmo cenário contra dois códigos.
- **Entradas:** os casos normais e as classes de bug de `rules/testing.md` que se aplicam.
- **Bug encontrado:** o teste afirma o comportamento atual, o nome diz isso, e **abre-se um card de bug na hora**, seguindo a seção "Bug encontrado na migração", mais abaixo. Não corrija.
- **SQLite × MySQL:** se o comportamento depende de collation, `NaN` ou `affectedRows`, diga no nome do teste.

**Saída:** 1 a 2 PRs só de teste, sem tocar no legado.
**Pronto quando:** todo ponto que grava no inventário tem pelo menos um cenário verde com o driver legado.

## 2. Construir

**Objetivo:** o submódulo completo, testado, sem ninguém chamar.

- Camadas: `domain` (model, values, ports), `application`, `repository` com mapper, `infrastructure`, `access`, `api/`, mais config, enum de logs e erros. Ver [receitas.md](receitas.md).
- Registrado no `WhatsappModule`. Não é feature flag: não existe `if`, só código ainda sem chamador.
- Entra o driver da fachada e a **mesma suíte** passa a rodar com os dois:

```ts
const drivers: BlockContactDriver[] = [legacyBlockDriver, contactsApiDriver];
```

- Testes unitários do domain junto.
- PRs de 200 a 400 linhas, nesta ordem: domain → repository e mapper → application e api → access e registro.

**Pronto quando:** caracterização verde com os dois drivers e `npm run lint:whatsapp` sem erro.

## 3. Trocar

**Objetivo:** todo ponto que grava passa a usar o submódulo.

Um PR por ponto do inventário:

1. O chamador injeta o token do `api/` (de dentro do módulo) ou de `public/` (de fora) e chama a operação de negócio.
2. O trecho legado que ficou sem uso é apagado no mesmo PR.
3. Se o arquivo não lê mais nada do legado, ele sai da lista de exceções no mesmo PR.
4. Quando o código legado de um cenário some, o driver legado dele também some.
5. Se o fluxo passa por algo ainda legado, o chamador legado continua orquestrando: chama o módulo e depois o legado ([coexistencia.md](coexistencia.md), situação 2).

**Pronto quando:** nenhum código legado grava nas tabelas assumidas. Inventário todo marcado; busca pelos métodos de escrita antigos vazia.

## 4. Drenar (só quando a capacidade usa fila)

**Por quê:** as filas do módulo têm nome novo (`whatsapp.<sub>.<ação>`) e rodam só na frota
`WHATSAPP_PIPELINE`. No instante do deploy, a fila antiga ainda tem jobs: em espera, em backoff de
retry ou agendados. Sem o processor antigo, eles ficariam parados para sempre, sem erro.

1. O processor novo entra no passo 2; no passo 3, quem produz passa a enfileirar na fila nova.
2. O processor antigo **continua registrado** no deploy da milestone e consome o que sobrou no formato antigo. Nada de traduzir payload.
3. Depois do deploy em produção, confira a fila antiga zerada pelo gauge `bullmq_job_count`, incluindo `delayed`.
4. Cron: o job scheduler antigo continua criando jobs até ser **removido do Redis**. Apagar o código não basta.
5. Um PR pequeno apaga o processor antigo e o registro da fila, logo depois do deploy.

**Pronto quando:** fila antiga vazia, scheduler antigo removido e nenhum dos dois no código.

## 5. Fechar

- [ ] Número da lista de exceções antes e depois, no PR da milestone
- [ ] Legado sem uso apagado
- [ ] Caracterização sem driver: `describe.each` e o objeto do driver removidos, o teste chama o módulo direto e vira spec normal ao lado do código (`characterization/` deixa de existir). Os cenários ficam como regressão
- [ ] `overview.md` e `log.md` do submódulo no bundle OKF
- [ ] Métricas antes e depois: p95 do envio, latência do webhook, pool de conexões
- [ ] Handoff de QA no card do épico: o que muda e o que não pode mudar, com o número medido (`flow-coding/qa-handoff.md`)
- [ ] Milestone → staging → master; canary em envio pela fila e recebimento
- [ ] Rollback é reverter o merge da milestone

## Bug encontrado na migração

Vale para qualquer passo: caracterização, construção, troca ou revisão de PR. A migração preserva
o comportamento (D12); o bug é registrado para ser resolvido depois, fora da milestone.

1. **Confirme que é bug, não regra.** Comportamento estranho com motivo de negócio não é bug: se houver dúvida, pergunte antes de abrir.
2. **Escreva o cenário que prova o bug** na suíte de caracterização, afirmando o comportamento atual, com o card no nome: `it('preserva bug #<n>: bloqueio ignora telefone com espaço', …)`.
3. **Abra o card** com o fluxo de criação de cards de bug do repositório (`flow-coding/issue-tracker.md`, template `bug-report.yml`):
    - título: o sintoma, como o cliente veria;
    - body: comportamento atual, comportamento esperado, onde está no código (`caminho:linha`), o nome do teste que o prova e a milestone em que foi achado;
    - labels: `work: bug`, a label do epic e `ai-assisted` quando aplicável;
    - **sub-issue do epic** do módulo WhatsApp, não da task que o achou;
    - Priority e Size quando der para avaliar; Estimate fica com o time.
4. **Volte ao trabalho.** O PR da milestone cita o card na descrição, na seção de bugs preservados.
5. **Quando o bug for corrigido**, no card dele e fora da milestone, o mesmo teste muda de afirmação e perde o "preserva bug" do nome.

O inventário da milestone mantém a lista dos cards abertos; o handoff de QA cita todos.

## Branches

- `milestone/<epic>-whatsapp-<fase>` sai de master; tasks são PRs para ela.
- Master entra todo dia, por merge, sem rebase.
- Até cerca de 3 semanas; vai inteira para produção.
