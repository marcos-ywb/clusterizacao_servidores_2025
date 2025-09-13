# Relatório de atividade: Implementação de aplicação Flask distribuída em Kubernetes

## 1. Introdução:
Este relatório descreve, de forma detalhada, a implementação e o teste de uma aplicação **Flask** para simulações de Monte Carlo, distribuída em múltiplos pods utilizando **Kubernetes**. O objetivo principal consistiu em fazer o deploy da aplicação com **Docker** e **Kubernetes**, testar os endpoints existentes que calculam estimativas de **π** e da **área de um quadrado inscrito em um círculo** e modificar o código conforme o que se pede, tanto em modo single pod quanto em modo distribuído.

Foram explorados conceitos de containerização com **Docker**, orquestração com **Kubernetes**, além de técnicas de distribuição de cálculos entre réplicas de pods.

## 2. Ambiente de desenvolvimento:
- **Sistema Operacional:** Ubuntu 22.04 (VM)
- **Minikube:** v1.37.0
- **kubectl:** v1.30.0
- **Docker:** v28.4.0
- **Python:** v3.12.3
- **Flask:** v2.2.5
- **Bibliotecas Python:** `os`, `socket`, `random`, `math`, `jsonify`, `request`

## 3. Clonagem do repositório:
O projeto foi obtido a partir do repositório remoto:

```bash
git clone -b master https://github.com/LuisVCSilva/clusterizacao_servidores_2025.git
cd clusterizacao_servidores_2025
```

## 4. Endpoints da aplicação:
| Endpoint                          | Método | Objetivo                                                                                       | Observações                                                     |
|----------------------------------|--------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| `/`                               | GET    | Retornar mensagem de boas-vindas e lista de endpoints disponíveis                               | Útil para verificar se o app está rodando                       |
| `/docker-info`                    | GET    | Retornar informações do container Docker atual                                                 | Retorna hostname, diretório de trabalho e primeiras variáveis de ambiente |
| `/montecarlo/<n>`                 | GET    | Estimar π usando Monte Carlo em single CPU (local, dentro de 1 container)                     | n → número de amostras                                          |
| `/montecarlo-distributed/<n>`     | GET    | Estimar π usando Monte Carlo distribuído entre todos os pods                                   | n → número de amostras; resultados parciais devem ser agregados externamente |
| `/montecarlo-square/<n>`          | GET    | Estimar a área de um quadrado inscrito em um círculo usando Monte Carlo                        | Funciona tanto em single pod quanto distribuído; retorna proporção de pontos e área estimada |

- A rota **`/montecarlo-square/<n>`** foi criada pelo autor desta atividade para cumprir o requisito de estimar a área de um quadrado inscrito em um círculo usando Monte Carlo distribuído.

## 5. Passo a passo utilizado:
### 1. Instalação do Docker
```bash
# Remover versões antigas (se houver)
sudo apt-get remove docker docker-engine docker.io containerd runc -y

# Atualizar lista de pacotes
sudo apt-get update -y

# Instalar dependências
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Adicionar chave GPG oficial do Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adicionar repositório do Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualizar e instalar Docker Engine + CLI + Compose
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Ativar serviço e permitir uso sem sudo (opcional)
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Testar instalação
docker --version
docker run hello-world
```

### 2. Instalação do kubectl
```bash
# Baixar versão estável mais recente
curl -LO "https://dl.k8s.io/release/$(curl -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Dar permissão de execução
chmod +x kubectl

# Mover para pasta do sistema
sudo mv kubectl /usr/local/bin/

# Testar instalação
kubectl version --client
```

### 3. Instalação do Minikube
```bash
# Baixar binário do Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Instalar no sistema
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Testar instalação
minikube version
```

- **Dica:** Reinicie o sistema ou use `newgrp docker` para garantir acesso ao Docker sem `sudo`.

### 4. Iniciar cluster Minikube
```bash
# Iniciar o cluster
minikube start --driver=docker

# Verificar status
minikube status
kubectl get nodes
```

### 5. Ativar o Docker do Minikube
```bash
eval $(minikube docker-env)
```

### 6. Buildar a imagem
```bash
docker build -t flask-montecarlo:latest .
```

### 7. Aplicar o YAML (Deployment + Service)
```bash
kubectl apply -f kube-flask-montecarlo.yaml
```

### 8. Verificar se os pods subiram
```bash
kubectl get pods -l app=flask-montecarlo -o wide
```

### 9. Verificar se o serviço foi criado
```bash
kubectl get svc flask-montecarlo-service
```

### 10. Acessar a aplicação
```bash
# Buscar a url da aplicação
minikube service flask-montecarlo-service --url

# Retorno
http://192.168.49.2:32319

# Testar os endpoints
curl http://192.168.49.2:32319/
curl http://192.168.49.2:32319/docker-info
curl http://192.168.49.2:32319/montecarlo/<int:n>
curl http://192.168.49.2:32319/montecarlo-distributed/<int:n>
curl http://192.168.49.2:32319/montecarlo-square/<int:n>
```

- Também é possível testar os endpoints via navegador utilizando o comando `minikube service flask-montecarlo-service`, ele abrirá automaticamente o navegador apontando para um dos pods pelo IP do Minikube.

## 6. Problemas encontrados e resolução:
Durante a implementação da rota `/montecarlo-distributed/<n>`, foi observado que a rota **não funcionava corretamente** ao ser testada via `curl` ou navegador.  

Após análise, constatou-se que o problema **não estava no código Python**, mas sim na **configuração das variáveis de ambiente no Kubernetes**, especialmente a variável `POD_INDEX`.  
- O valor retornado por `fieldRef: metadata.name` nem sempre era diretamente um número, o que causava erros ao tentar converter para `int`.  
- A solução foi implementar um **fallback seguro**, que extrai um índice numérico a partir do nome do pod, garantindo que cada pod saiba sua “posição” para calcular sua parte das amostras.

**Trecho do código corrigido:**

```python
pod_name = os.getenv("POD_INDEX", "0")
try:
    pod_index = int(pod_name.split('-')[-1], 36) % replicas
except ValueError:
    pod_index = 0  # fallback se não conseguir extrair
```
---
Durante a execução dos testes automatizados, surgiu o seguinte erro:
```vbnet
TypeError: required field "lineno" missing from alias
```
Após investigação, verificou-se que o problema não estava no código da aplicação, mas sim na compatibilidade entre Python 3.12 e algumas versões do pytest e plugins, como o pytest-cov.
```bash
# Atualizar pytest e pytest-cov
pip install --upgrade pytest pytest-cov

# Remover arquivos de cache compilados
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

- **Observações:** Recomenda-se utilizar `pytest` >= 8.3 e `pytest-cov` >= 4.0 para compatibilidade com Python 3.12.

Após essas alterações, os testes automatizados passaram a executar corretamente, permitindo validar tanto a função Monte Carlo quanto os endpoints da aplicação.

## 7. Observações:
Durante o desenvolvimento e deploy da aplicação, foram identificados alguns pontos importantes que merecem destaque:

### 1. Rebuild da imagem Docker
- Sempre que alterações no código fonte `(app.py)` forem realizadas, é necessário reconstruir a imagem Docker e reaplicar o deployment para que as mudanças sejam refletidas nos pods.
```bash
docker build -t flask-montecarlo:latest .
kubectl rollout restart deployment flask-montecarlo-deployment
```

### 2. Teste dos endpoints
- Para acessar a aplicação, deve-se obter a URL do serviço via Minikube.
```bash
minikube service flask-montecarlo-service --url
```
- Em seguida, é possível testar os endpoints com curl ou navegador.
- **Observação:** os endpoints distribuídos `(/montecarlo-distributed/<n> e /montecarlo-square/<n>)` retornam resultados parciais por pod. Para obter a estimativa total, é necessário agregar os resultados externamente.

### 3. Fallback de `pod_index`
- Para garantir funcionamento em todos os pods, foi implementado um **fallback seguro** para `pod_index`, caso a conversão do nome do pod falhe.

### 4. Uso correto das variáveis de ambiente no Kubernetes
- `POD_REPLICAS` define o número de réplicas do deployment e é utilizada para distribuir as amostras entre os pods.

- `POD_INDEX` foi obtido via `fieldRef: metadata.name`. Inicialmente, esta variável não era diretamente numérica, sendo necessário extrair o índice numérico com um fallback seguro para evitar erros de conversão.

### 5. Importância da replicação
- Ao utilizar múltiplos pods, cada pod calcula apenas sua fração das amostras.
- Essa abordagem permite paralelização do cálculo, tornando a estimativa mais eficiente em cenários de alto volume de amostras.

## 8. Testes automatizados
- Para efetuar os testes automatizados foi necessário criar um ambiente virtual para a instalação das dependências de forma isolada.

```bash
# Criar o ambiente virual venv
python3 -m venv .venv

# Ativar o ambiente
source .venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt

# Rodar o teste automatizado
pytest --cov=app test_app.py
```

## 9. Evidências
### 1. Build da imagem Docker
![docker build](images/docker/build-image.png)

### 2. Verificação dos containers em execução
![docker ps](images/docker/docker-ps.png)

### 3. Logs do Docker
![docker logs](images/docker/docker-logs.png)

### 4. Pods criados no cluster Kubernetes
![kubectl get pods](images/kubectl/kubectl-get-pods.png)

### 5. Service criado no cluster
![kubectl get svc](images/kubectl/kubectl-get-svc.png)

### 6. URL do serviço obtida via Minikube
![minikube service url](images/minikube/minikube-service-url.png)

### 7. Teste dos endpoints via curl
![curl endpoint](images/curl/curl-main.png)
![curl endpoint](images/curl/curl-docker-info.png)
![curl endpoint](images/curl/curl-montecarlo.png)
![curl endpoint](images/curl/curl-montecarlo-distributed.png)
![curl endpoint](images/curl/curl-montecarlo-square.png)

### 8. Execução do agregador distribuído
![aggregator](images/montecarlo-aggregator.png)
- **Observação:** Comando utilizado para rodar o aggregator: `SERVICE_HOST=192.168.49.2 SERVICE_PORT=32319 POD_REPLICAS=3 python3 montecarlo_aggregator.py`

### 9. Resultado dos testes automatizados
![pytest](images/testes-automatizados.png)

## 10. Conclusão
A atividade demonstrou de forma prática a aplicação de conceitos de containerização e orquestração utilizando Docker e Kubernetes, aliada ao desenvolvimento de uma aplicação Flask capaz de realizar cálculos distribuídos de Monte Carlo. Foi possível observar claramente como a replicação de pods permite a paralelização de tarefas, tornando os cálculos mais eficientes e escaláveis.

Além disso, o workflow demonstrou a importância de etapas como:
- Rebuild da imagem Docker sempre que o código é alterado;
- Reaplicação do deployment para refletir alterações nos pods;
- Agregação dos resultados parciais obtidos por cada pod em cálculos distribuídos;
- Uso correto das variáveis de ambiente para garantir consistência e confiabilidade nos cálculos.

Em resumo, o trabalho reforçou o entendimento sobre a integração entre desenvolvimento de aplicações, Docker e Kubernetes, evidenciando como práticas de containerização e orquestração podem ser aplicadas em cenários de computação distribuída para melhorar desempenho e confiabilidade. A experiência também ressaltou a importância do planejamento e da verificação detalhada das configurações do ambiente para evitar problemas durante o deploy de aplicações distribuídas.
