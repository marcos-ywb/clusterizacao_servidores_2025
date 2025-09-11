# Flask Monte Carlo

Este projeto é uma aplicação Flask que realiza simulações Monte Carlo para estimativa de \$\pi\$, podendo rodar tanto **localmente em Docker** quanto de forma **distribuída em Kubernetes**.

## Atividade prática NF2

### O que os alunos devem fazer:

1. Fazer o **deploy da aplicação** usando Docker e Kubernetes.
2. Testar todos os **endpoints**:

   * `/docker-info` para verificar informações do container.
   * `/montecarlo/<n>` para testar a simulação em CPU única.
   * `/montecarlo-distributed/<n>` para testar a simulação distribuída em múltiplos pods.
3. Modificar o código para **adicionar um novo endpoint** que execute uma variação da simulação Monte Carlo (exemplo: estimativa de área de uma função ou outra forma geométrica).
4. Utilizar o script `montecarlo_aggregator.py` ou criar sua própria lógica para **agregar resultados distribuídos**.

### Critérios de avaliação:

* Correto **deploy** da aplicação em Docker e Kubernetes.
* Funcionamento correto de todos os **endpoints**.
* Capacidade de **modificação do código** para criar um novo endpoint funcional.
* Clareza e organização do **código e testes**.
* Uso correto das ferramentas de container e cluster (Docker, Minikube/Kubernetes).

### Sugestão de modificação no código:

* Criar um endpoint `/montecarlo-square/<n>` que estima a área de um quadrado inscrito em um círculo usando Monte Carlo.
* Retornar tanto a estimativa da área quanto a proporção de pontos dentro da área esperada.
* Garantir que o endpoint funcione tanto em single CPU quanto em modo distribuído nos pods.


---

## 📝 Estrutura do projeto

```
.
├── app.py                        # Aplicação Flask
├── Dockerfile                     # Dockerfile para container
├── requirements.txt               # Dependências Python
├── Makefile                       # Comandos automatizados (build, run, test)
├── kube-flask-montecarlo.yaml     # Deployment e Service para Kubernetes
├── montecarlo_aggregator.py       # Script Python para agregar resultados distribuídos
├── test_app.py                     # Testes unitários / integração com pytest
├── README.md
└── minikube-linux-amd64           # Binário Minikube (opcional)
```

---

## 🚀 Endpoints disponíveis

* **`/docker-info`**
  Retorna informações do container atual (hostname, diretório atual e variáveis de ambiente).

* **`/montecarlo/<n>`**
  Executa uma simulação Monte Carlo com `n` amostras em **CPU única**.

* **`/montecarlo-distributed/<n>`**
  Executa uma simulação Monte Carlo distribuída em múltiplos pods, retornando a estimativa parcial de cada pod.

---

## 🐳 Docker

### Build da imagem

```
docker build -t flask-montecarlo:latest .
```

### Rodar o container

```
docker run -p 8080:8080 flask-montecarlo
```

### Testar endpoints

```
curl http://127.0.0.1:8080/docker-info
curl http://127.0.0.1:8080/montecarlo/1000000
```

---

## ☸️ Kubernetes (Minikube ou cluster local)

### Aplicar Deployment e Service

```
kubectl apply -f kube-flask-montecarlo.yaml
kubectl get pods
kubectl get svc
```

### Acessar endpoints

* **Port-forward**

```
kubectl port-forward service/flask-montecarlo-service 8080:8080
curl http://127.0.0.1:8080/montecarlo-distributed/1000000
```

* **Minikube service**

```
minikube service flask-montecarlo-service --url
curl http://<URL>/montecarlo-distributed/1000000
```

> Observação: cada pod calcula apenas sua parte (`pi_partial`). Para obter o valor final, use `montecarlo_aggregator.py` para agregar os resultados.

---

## ✅ Testes

```
make test
```

Executa os testes unitários com `pytest` e cobertura de código.

---

## 🛠 Makefile

Alguns comandos úteis:

* `make install` - instala dependências Python
* `make lint` - verifica estilo e linting do código
* `make build` - build da imagem Docker
* `make run` - roda container Docker local
* `make invoke` - testa endpoint Monte Carlo localmente
* `make run-kube` - aplica manifestos Kubernetes

