# RLS e grants na migração

Exemplo reduzido de tabela privada por pessoa. Não é o modelo de catálogo compartilhado, projeto
ou capacidades do OS. `os_app` ilustra a role de aplicação; o nome real ainda depende da configuração.
A role dona executa este SQL. A role de aplicação deve ser provisionada sem superuser/BYPASSRLS,
sem ownership e sem poder assumir a dona. Nunca conceda a role dona à aplicação.

```sql
CREATE TABLE private_records (
    id text PRIMARY KEY,
    tenant_id text NOT NULL,
    person_id text NOT NULL,
    value text NOT NULL
);

ALTER TABLE private_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY private_records_scope ON private_records
    TO os_app
    USING (
        tenant_id = nullif(current_setting('app.tenant_id', true), '')
        AND person_id = nullif(current_setting('app.person_id', true), '')
    )
    WITH CHECK (
        tenant_id = nullif(current_setting('app.tenant_id', true), '')
        AND person_id = nullif(current_setting('app.person_id', true), '')
    );

GRANT USAGE ON SCHEMA public TO os_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON private_records TO os_app;
```

As tabelas declaradas no schema são geradas pelo Kit; não copie `CREATE TABLE` duplicado para outra
migração. Acrescente a policy e grants em SQL revisado, mantendo a ordem após criação da tabela.
Adapte o schema físico e os grants aos recursos reais; não use `GRANT ALL` global. Policies de outros
escopos exigem as regras de ACL correspondentes; esta policy não autoriza compartilhamento.

`current_setting(..., true)` tolera configuração ausente; `nullif(..., '')` também trata o valor
vazio após reuso de conexão. A comparação não fica verdadeira sem principal. A UoW usa os mesmos
nomes com `set_config(..., true)` parametrizado dentro da transação e no mesmo executor.
`USING` limita linhas visíveis/alteráveis; `WITH CHECK` limita os valores novos de insert/update.

A dona das tabelas normalmente ignora RLS; superuser/BYPASSRLS sempre ignora. `FORCE ROW LEVEL
SECURITY` pode sujeitar a dona às policies, mas não é a configuração de duas roles descrita aqui
e não torna um teste como superuser válido. Execute as verificações de isolamento conectado como
aplicação e confirme ownership/grants. Os nomes de role/GUC do exemplo não são decisão de implantação.
