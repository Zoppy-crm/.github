---
name: test-audit
description: Use when reviewing whether an existing spec actually verifies the code it covers — a PR that touches .spec.ts files, a file that just had a bug fixed despite having tests, "esse teste pega o bug?", "revisa esse teste", "o que falta nesse spec", "lacunas do teste", coverage green and a defect escaped anyway.
---

# Test audit

## Princípio

Cobertura diz que a linha rodou, não que um teste falharia se a saída estivesse errada. A pergunta desta skill é uma só: **supondo que o código tem um defeito que o spec não pega, qual é ele?**

Medido em bugs reais que escaparam de specs existentes, essa pergunta, feita de forma direta e com entrada concreta, apontou o defeito em cerca de 1 a cada 3. Um procedimento mais longo (catálogo de classes, tabela completa) não aumentou esse número. Por isso a skill é curta: faça a pergunta bem.

## Como fazer

Leia o arquivo-fonte, o spec e as factories ou helpers de seed que o spec usa. Depois liste **exatamente 5 lacunas**, da mais para a menos provável. Cada uma com:

- **Entrada ou estado concreto** que o spec não exercita ou não verifica. Valor, não categoria: `fullName = '   '`, não "testar strings".
- **O que o código faz** com essa entrada, lendo o código, e se isso parece errado.
- **Por que o spec não pega:** não exercita; exercita, mas a asserção não distingue certo de errado; ou o spec afirma algo que pode estar errado.

## Onde costuma estar

- Fixture que usa um valor só em todos os testes para um campo que o código lê.
- Asserção fraca sobre valor calculado: `toBeDefined`, `length > 0`, `toHaveBeenCalled` sem argumento.
- Teste que afirma recusa, bloqueio, stub ou "não faz": confira se outra fonte (quem chama, o card, o outro sistema) concorda com esse esperado.
- Mock que aceita qualquer argumento, ou que pula a serialização que o real faz.

## O que não pega

Regra que ninguém escreveu, contrato com outro sistema, concorrência e estado que muda entre execuções raramente aparecem lendo só o arquivo e o spec. Se o card da feature existir, leia-o antes: é dali que vem o esperado certo.
