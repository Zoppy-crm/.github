# **Documento de Entrega Técnica para QA**

Este documento tem como objetivo **padronizar o conteúdo mínimo necessário para a documentação técnica e funcional das tarefas e features** em desenvolvimento.

Ele serve como **base obrigatória para validação e aprovação das entregas** pelo time de QA e demais áreas envolvidas.

A intenção aqui **não é engessar o formato**, mas **garantir que as informações essenciais estejam sempre presentes** — especialmente os **critérios de aceite**, que são indispensáveis para o processo de homologação e deploy.

Cada desenvolvedor pode estruturar o documento conforme seu estilo pessoal ou conforme as particularidades da tarefa, **desde que o conteúdo obrigatório seja contemplado** de forma clara, objetiva e rastreável.

Em resumo: o **foco está na qualidade e completude das informações**, não no layout do documento.

### **1\. Descrição Principal da Tarefa**

A tarefa tem como principal objetivo melhorar o processo de inadimplência e a experiência dos usuários, garantindo validação e sincronização dos dados de pagamento. Nessa nova funcionalidade, o usuário consegue alterar a forma de pagamento, adicionar um cartão de crédito e realizar o pagamento. Além disso, enquanto ele estiver inadimplente, ele não consegue navegar no sistema.

---

### **2\. Funcionalidade Principal da Tarefa (Exemplo)**

-   Usuário inadimplente \> modal de faturas abre ( até 2 faturas ) \> usuário seleciona uma fatura para pagar ou alterar método de pagamento
    -   Caso altere o método de pagamento, ele deve selecionar cartão de crédito ou pix, podendo também, adicionar um novo cartão
    -   Caso contrário, o pagamento deve ser realizado com a forma de pagamento padrão da empresa.
-   Caso o usuário tenha mais de 2 faturas ( caso improvável em produção ), abrirá uma tela com as mesmas funcionalidades do modal.

---

### **3\. Critérios de Aceite (Exemplo)**

-   Deve ser possível o pagamento apenas em Pix e em Cartão de Crédito
-   Deve ser possível adicionar um novo cartão
-   Cada fatura deve ser paga individualmente
-   O modal de inadimplência deve aparecer apenas caso:
    -   o usuário tem a feature flag ativada
    -   o campo **inadimplent** deve estar **verdadeiro** na tabela Companies
    -   o usuário tenha até duas faturas ( caso contrário, deverá direcionar a uma página com todas as faturas )
-   Caso o método de pagamento padrão seja Boleto, o usuário deve ser obrigado a alterar a forma de pagamento.

---

### **4\. Rotas de API Utilizadas ou Alteradas (Exemplo)**

-   Get  
    /api/payment-methods/last-used  

-   Get  
    /api/bills/transaction-status

-   Put  
    /api/bills/update-payment-method  

-   Get  
    /api/companies/payment-profile

-   Get  
    /api/companies/payment-profile/list  

-   Put  
    /api/companies/status/refresh  

-   Put  
    /api/companies/payment-method  

-   Get  
    /api/bills/pending

-   Put  
    /api/bills/pay

---

### **5\. Filas/Serviços Assíncronos Envolvidos _(se aplicável)_**

    Não há serviços assíncronos.

---

### **6\. Tabelas do Banco de Dados Utilizadas ou Alteradas (Exemplo)**

-   Companies: obtemos a informação do método de pagamento atual
-   PaymentMethod: a partir dessa, conseguimos obter os dados do cartão de crédito da company.
-   Invoices: nessa tabela, obtemos a informação da fatura, valor e produtos.
-   Charges: essa tabela apresenta cada cobrança gerada para uma fatura. Por exemplo, ao alterar o cartão de crédito da fatura, é necessário gerar uma nova cobrança para aquela fatura.
-   Transactions: é cada tentativa de pagamento de uma cobrança.

---

### **7\. Feature Flags ou Configs (Exemplo)**

-   Feature Flag **account_temporarily_suspended_payment_details** deve estar habilitada para visualizar a nova jornada de inadimplência

---

### **8\. Permissões ou Regras de Acesso**

    Não há controle de permissão

---

### **9\. Cenários de Teste Esperados / Dicas para QA (Exemplo)**

-   Verificar se as mensagens de erro/sucesso enviados pela vindi estão sendo cadastradas no banco de dados e renderizadas para o usuário
-   Realizar pagamento com cartão de crédito inválido
-   Realizar pagamento com cartão de crédito válido
-   Realizar pagamento via pix
-   Verificar se o Qr Code está sendo renderizado para o Pix
-   Verificar se o código copia e cola do Pix está funcionando.
-   O pagamento de uma fatura deve corresponder exclusivamente à fatura selecionada.
-   Realizar cadastro de um novo cartão
-   Testar as possibilidades de o usuário não conseguir utilizar o sistema caso esteja inadimplente.

---

### **10\. Implicações Técnicas / Possíveis Regressões**

---

### **✅ Checklist Final Antes de Enviar para QA**

-   \[ X \] Código está (DE FATO) em ambiente de homologação (Pipeline rodou sem falhas).
-   \[ X \] Todos os critérios de aceite do documento foram cumpridos.
-   \[ X \] Rotas e tabelas documentadas.
-   \[ X \] Testes manuais básicos realizados (Para garantir que o mínimo esteja funcional).
-   \[ X \] Documentação preenchida e enviada para QA.
-   \[ X \] Cards da esteira relacionados aos testes foram movimentados para a coluna correta (Staging/Mirror).
