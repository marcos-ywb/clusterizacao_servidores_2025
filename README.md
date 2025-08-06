# Avaliação de Checagem — MPI em Laboratório
## Aplicações de clusterização em servidores

**Tema:** Comunicação entre processos com MPI (Scatter, Gather, rank, size)  
**Aluno:** _Marcos Mello_  
**Data:** 05/08/2025  

---

###  Objetivo

Executar, analisar e modificar um programa MPI que distribui dados entre processos, realiza cálculos locais e coleta os resultados para ordenação.

---

###  Arquivo base

O código que você deve utilizar está nesse diretorio:

```
media_mpi.c
```

Compile com:

```bash
mpicc media_mpi.c -o media_mpi
```

Execute com:

```bash
mpirun -np 4 ./media_mpi
```

---

### Parte 1 — Execução básica

#### 1.1. Saída esperada

Execute o programa com 4 processos. Copie aqui a saída do terminal:

```
Processo 0 enviando dado: 42 para processo 1
Processo 1 recebeu dado: 42 do processo 0
```

---

###  Parte 2 — Análise de funcionamento

#### 2.1. O que faz `MPI_Scatter` neste código?

_Resposta:_
O Código em questão não utiliza `MPI_Scatter`, ele utiliza a comunicação ponto-a-ponto (`MPI_Send` e `MPI_Recv`);

---

#### 2.2. Qual o papel de `MPI_Gather`?


_Resposta:_
Nesse código em específico, não há nenhum papel para o `MPI_Gather` pois só há troca de dados entre dois processos específicos. O `MPI_Gather` é utilizado com o intuito de reunir dados de todos os processos em um só (normalmente o processo 0);

---

#### 2.3. Por que a ordenação das médias acontece apenas no processo 0?

_Resposta:_
Pois é no processo 0 que todos os dados são reunidos usando exemplos de funções citadas acima, como `MPI_Gather` ou `MPI_Recv` em loop. Outros processos possuem acesso apenas aos seus dados locais e não ao conjunto completo de dados

---

###  Parte 3 — Modificação

#### 3.1. Modifique o código para que **cada processo envie também seu maior valor local**, além da média.

Use `MPI_Gather` para coletar ambos os dados no processo 0.

 - Faça um **commit com sua modificação** e anexe abaixo o arquivo completo.

---

### 3.2. Copie aqui a saída do seu programa modificado:

```
[Processo 0] Dados coletados:
Processo 0 -> Média: 1.50 | Máximo: 10.00
Processo 1 -> Média: 3.00 | Máximo: 20.00
Processo 2 -> Média: 4.50 | Máximo: 30.00
Processo 3 -> Média: 6.00 | Máximo: 40.00
```

---

### Análise com utilitários Linux

#### 4.1. Use o comando `time` para medir o tempo de execução do programa com 2, 4 e 6 processos.

Anote abaixo:

| Processos | Tempo (real) |
|-----------|--------------|
| 2         |   0m0.348s   |
| 4         |  	0m0.372s   |
| 6         |   0m0.397s   |

#### 4.2. Use `htop` ou `top` para observar o uso de CPU. O uso foi balanceado entre os processos?

_Resposta:_
O uso da CPU foi **relativamente balanceado entre os processos MPI**, como esperado em aplicações simples onde cada processo realiza operações semelhantes. Ao observar pelo `top`, é possível ver que os processos MPI estão distribuídos entre os núcleos disponíveis, cada um utilizando uma fração próxima da CPU, indicando uma **boa distribuição de carga**.

---

#### 4.3. Use `strace`, `taskset` ou `MPI_Wtime` para investigar comportamento adicional do programa. Comente algo que tenha achado interessante:

_Resposta:_

---

### Observações

- Faça commits frequentes com mensagens claras.
- Crie um `commit` final com a tag `atividade-finalizada`.
- Envie o link do seu repositório *forkado* com a atividade completa para luis.professor@uniatenas.edu.br

---

**Boa prática!**
