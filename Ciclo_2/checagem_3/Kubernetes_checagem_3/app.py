import os
import socket
import random
import math
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

#==============================================================================================#
#===[    FUNÇÃO DE SIMULAÇÃO MONTE CARLO    ]==================================================#
#==============================================================================================#
def monte_carlo_pi(num_samples: int) -> float:
    inside_circle = 0
    for _ in range(num_samples):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1.0:
            inside_circle += 1
    return (4.0 * inside_circle) / num_samples

#==============================================================================================#
#===[    ENDPOINTS    ]========================================================================#
#==============================================================================================#

#===[    MAIN    ]=============================================================================#
@app.route('/')
def index():
    return jsonify({
        "message": "Olá do app Flask + Kubernetes!",
        "endpoints": [
            "/docker-info",
            "/montecarlo/<n>",
            "/montecarlo-distributed/<n>"
        ]
    })

#===[    DOCKER INFO    ]======================================================================#
@app.route('/docker-info')
def docker_info():
    """Retorna informações do container Docker atual"""
    info = {
        "hostname": socket.gethostname(),
        "cwd": os.getcwd(),
        "env": dict(list(os.environ.items())[:10])  # só os 10 primeiros envs
    }
    return jsonify(info)

#===[    MONTECARLO    ]=======================================================================#
@app.route('/montecarlo/<int:n>')
def montecarlo_single(n):
    """Monte Carlo single CPU (local, dentro de 1 container)"""
    pi_estimate = monte_carlo_pi(n)
    return jsonify({
        "samples": n,
        "pi_estimate": pi_estimate,
        "mode": "single-cpu"
    })

#===[    MONTECARLO DISTRIBUTED    ]===========================================================#
@app.route('/montecarlo-distributed/<int:n>')
def montecarlo_distributed(n):
    """
    Monte Carlo distribuído: divide o total de amostras (n)
    entre todos os pods (réplicas) do deployment.
    """
    replicas = int(os.getenv("POD_REPLICAS", "1"))
    pod_name = os.getenv("POD_INDEX", "0")
    
    try:
        pod_index = int(pod_name.split('-')[-1], 36) % replicas
    except ValueError:
        pod_index = 0  # fallback se não conseguir extrair
    
    per_pod = n // replicas
    pi_estimate = monte_carlo_pi(per_pod)
    
    return jsonify({
        "samples_total": n,
        "samples_this_pod": per_pod,
        "replicas": replicas,
        "pod_index": pod_index,
        "pi_partial": pi_estimate,
        "note": "Resultados devem ser agregados fora (ex: via Service + client aggregator)."
    })

#===[    MONTECARLO SQUARE    ]================================================================#
@app.route('/montecarlo-square/<int:n>')
def montecarlo_square(n):
    """
    Estima a área de um quadrado inscrito em um círculo usando Monte Carlo.
    Funciona tanto em single pod quanto em modo distribuído.
    """
    num_replicas = int(os.getenv("POD_REPLICAS", "1"))
    nome_pod = os.getenv("POD_INDEX", "0")
    
    try:
        indice_pod = int(nome_pod.split('-')[-1], 36) % num_replicas
    except ValueError:
        indice_pod = 0

    amostras_por_pod = n // num_replicas

    pontos_no_quadrado = 0
    for _ in range(amostras_por_pod):
        x, y = random.random() * 2 - 1, random.random() * 2 - 1
        if x**2 + y**2 <= 1:
            if abs(x) <= 1 / math.sqrt(2) and abs(y) <= 1 / math.sqrt(2):
                pontos_no_quadrado += 1

    proporcao_no_quadrado = pontos_no_quadrado / amostras_por_pod if amostras_por_pod > 0 else 0
    area_estimativa = proporcao_no_quadrado * math.pi

    return jsonify({
        "total_amostras": n,
        "amostras_este_pod": amostras_por_pod,
        "numero_replicas": num_replicas,
        "indice_pod": indice_pod,
        "pontos_no_quadrado": pontos_no_quadrado,
        "proporcao_no_quadrado": proporcao_no_quadrado,
        "area_estimativa": area_estimativa,
        "observacao": "Resultados parciais. Para estimativa total, agregue os pods."
    })

#==============================================================================================#
#===[    RUN    ]==============================================================================#
#==============================================================================================#
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

