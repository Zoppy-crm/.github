---
name: forms
description: >
    Padrão de formulário dos frontends React da Zoppy: react-hook-form + zod, schemas que recebem t,
    mappers formulário → API, estados de submit, erros da API, máscaras, campos sensíveis e
    acessibilidade. Use ao criar ou mudar formulário, validação, máscara ou tratamento de erro no submit.
    Triggers: "form", "formulário", "input", "campo", "validação", "zod", "react-hook-form", "useForm",
    "submit", "erro de campo", "máscara", "schema", "cartão", "CPF", "CNPJ".
---

# Formulários — frontends React

**react-hook-form + `@hookform/resolvers/zod` + zod.** O schema mora em
`features/<feature>/schemas/<nome>.schema.ts` e é a fonte única de formato e validação.

## Schema é uma factory que recebe `t`

A mensagem de validação é texto de interface, então passa pela tradução. O schema é uma função que
recebe `t` e devolve o schema; o tipo sai do `z.infer` do retorno:

```typescript
export const storeSiteSchema = (t: TFunction<'onboarding'>) =>
    z.object({
        url: z.string().trim().min(1, t('site.errors.required')).url(t('site.errors.invalid'))
    });

export type StoreSiteInput = z.infer<ReturnType<typeof storeSiteSchema>>;
```

`*.schema.ts` é isento de `typedef.variableDeclaration` para o `z.infer` continuar funcionando.

```typescript
const form: UseFormReturn<StoreSiteInput> = useForm<StoreSiteInput>({
    resolver: zodResolver(storeSiteSchema(t)),
    mode: 'onTouched',
    defaultValues: { url: '' }
});
```

Anote `form` com o tipo nomeado `UseFormReturn<Input>`. Sempre `defaultValues`, com `''` em vez de
`undefined`.

## Regras

1. **Espelhe a regra da API, não invente outra.** O front mostra antes do submit o que a API vai
   recusar; a API continua sendo a autoridade.
2. **`mode: 'onTouched'`**: valida ao sair do campo e depois a cada mudança. Campo não tocado não mostra
   erro.
3. **Normalize antes de validar** (trim, só dígitos em documento e telefone). A máscara é cosmética; o
   schema valida os dígitos.
4. **Use o `Field` de `shared/ui`**: ele liga `<label htmlFor>`, `aria-invalid`, `aria-describedby` e
   mostra o erro com `role="alert"`. Outros campos (seleção, documento, cartão) também moram em
   `shared/ui`; reuse antes de criar.
5. **Erro do servidor é do formulário por padrão.** Guarde o `ApiError` e mostre a mensagem traduzida
   pelo `errorType` acima do botão (ver data-fetching). Quando a regra do servidor é de um campo só,
   leve para o campo com `form.setError`.
6. **Submit desabilitado enquanto envia, dizendo o que acontece** ("Salvando…"), nunca um botão morto.
7. **O formulário não navega sozinho.** A página (ou o `onSubmit` que ela passa) decide o que vem
   depois. Use `form.handleSubmit(async (input) => …)` com `mutateAsync` e `try/catch`.
8. **`noValidate` no `<form>`**: quem valida e escreve a mensagem é o zod, não o navegador.
9. **30 linhas por função valem aqui também:** separe grupos de campos em componentes que recebem o
   `form` (`address-fields.tsx`, `card-fields.tsx`) e tire conversões do componente.

## Formulário ≠ corpo da API

O que o lojista digita raramente é o corpo da API (máscaras, `''` em opcional, campos divididos). A
conversão fica em `schemas/<nome>.mapper.ts`, com funções puras e spec próprio. O tipo do corpo vem dos
tipos gerados (via `types.ts`); o do formulário, do `z.infer`.

## Máscaras e formatos

Funções puras em `shared/lib/format/` (`maskCpfCnpj`, `maskPhoneBr`, `maskCep`, `maskCardNumber`,
`maskDigits`). CPF e CNPJ validam dígito verificador no schema; cartão valida Luhn.

## Campos sensíveis

-   Senha: `autoComplete="current-password"` ou `"new-password"`; e-mail de login com
    `autoComplete="username"`.
-   Código: `inputMode="numeric"` e `autoComplete="one-time-code"`.
-   Cartão: `cc-name`, `cc-number`, `cc-exp`, `cc-csc` e `inputMode="numeric"`.
-   **Nunca** registre valor de campo em log, nunca o coloque em query param, nunca o guarde em
    `localStorage`. Evento de analytics leva só propriedades da lista permitida, nunca valor de campo.
