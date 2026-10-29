# Roles e grants na migração

`os_owner` possui os objetos e aplica migrações; `os_app` executa HTTP/worker sem DDL, ownership,
superuser, criação de roles/bancos ou capacidade de assumir a dona. Bootstrap de roles é tarefa de
provisionamento privilegiado separada do runtime; segredos vêm de configuração, nunca deste SQL.
O Kit não modela os atributos completos e grants exigidos, por isso só esse bootstrap é manual.
As roles já provisionadas aparecem no schema como `pgRole("os_app").existing()` e
`pgRole("os_owner").existing()`, sem tentar recriá-las.

Exemplo para banco novo, executado pela credencial de provisionamento, não por `os_app`:

```sql
CREATE ROLE os_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE os_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOINHERIT;
```

A credencial de migração autorizada assume `os_owner`; não conceda essa associação a `os_app`.
Não use `CREATE ROLE` para recriar roles existentes; revise seu estado no provisionamento.
O provisionamento concede à dona os privilégios de banco/schema necessários para criar os objetos;
a migração dona os cria e depois concede à aplicação apenas os privilégios demonstrados pela fatia.
O schema físico abaixo é ilustrativo: use os nomes validados da implantação, não concatenação
SQL de identificadores recebidos do cliente.

```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO os_app;
GRANT SELECT, INSERT, UPDATE ON public."user", public.account TO os_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.session TO os_app;
GRANT SELECT, INSERT, DELETE ON public.verification TO os_app;
```

Esse conjunto corresponde a login Google e sessão; não habilita automaticamente unlink,
remoção de usuário ou qualquer plugin. Se fluxo habilitado precisar de update de verification
ou delete de user/account, comprove o uso e acrescente só o grant necessário. Restrinja colunas
quando compatível com os selects/retornos do adaptador. Tabelas de auth só são acessadas pelo
adaptador; não as exponha por repositórios/DTOs de negócio. Veja `os-auth-session`.

Para domínio, conceda por tabela/coluna/operação usada; para fila, uso do schema, DML e EXECUTE
somente das funções necessárias ao modo configurado. Não conceda CREATE no banco/schema, ALL,
TRUNCATE ou permissões sobre todos os objetos por conveniência. Revise os privilégios herdados de
PUBLIC: retire CREATE/TEMPORARY de banco e CREATE de schema que alcançariam `os_app`, além de
EXECUTE de funções administrativas do SDK que fazem DDL. Não relaxe esses privilégios no runtime.
O provisionamento de fila/partição usa a dona; não entregue funções administrativas como atalho.

Prove migração como dona e startup/operações como `os_app` em banco descartável, incluindo
falhas esperadas de DDL e de assumir `os_owner`. Grants são higiene de armazenamento. Autorização
de pessoas, times, capacidades e audiência é da aplicação, testada no domínio e na integração.
RLS só é possibilidade futura mediante decisão do dono, sem policies nesta fatia.
