from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Configuración de servicios
CASOS_SERVICE_URL = os.environ.get('CASOS_SERVICE_URL', 'http://casos-service:5001')
ESTADISTICAS_SERVICE_URL = os.environ.get('ESTADISTICAS_SERVICE_URL', 'http://estadisticas-service:5002')
GRAFICAS_SERVICE_URL = os.environ.get('GRAFICAS_SERVICE_URL', 'http://graficas-service:5003')

# Rutas del servicio de casos
@app.route('/api/casos', methods=['GET', 'POST'])
def casos_proxy():
    if request.method == 'GET':
        response = requests.get(f"{CASOS_SERVICE_URL}/api/casos", params=request.args)
    else:
        response = requests.post(f"{CASOS_SERVICE_URL}/api/casos", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/api/casos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def caso_proxy(id):
    if request.method == 'GET':
        response = requests.get(f"{CASOS_SERVICE_URL}/api/casos/{id}")
    elif request.method == 'PUT':
        response = requests.put(f"{CASOS_SERVICE_URL}/api/casos/{id}", json=request.json)
    else:
        response = requests.delete(f"{CASOS_SERVICE_URL}/api/casos/{id}")
    return jsonify(response.json()), response.status_code

# Rutas del servicio de estadísticas
@app.route('/api/estadisticas', methods=['GET'])
def estadisticas_proxy():
    response = requests.get(f"{ESTADISTICAS_SERVICE_URL}/api/estadisticas")
    return jsonify(response.json()), response.status_code

@app.route('/api/municipios/<nombre>/estadisticas', methods=['GET'])
def municipio_stats_proxy(nombre):
    response = requests.get(f"{ESTADISTICAS_SERVICE_URL}/api/municipios/{nombre}/estadisticas")
    return jsonify(response.json()), response.status_code

@app.route('/api/tendencia', methods=['GET'])
def tendencia_proxy():
    response = requests.get(f"{ESTADISTICAS_SERVICE_URL}/api/tendencia")
    return jsonify(response.json()), response.status_code

# Rutas del servicio de gráficas
@app.route('/api/datos-enfermedades', methods=['GET'])
def datos_enfermedades_proxy():
    response = requests.get(f"{GRAFICAS_SERVICE_URL}/api/datos-enfermedades")
    return jsonify(response.json()), response.status_code

# Rutas de frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/editar')
def editar():
    return render_template('editar.html')

@app.route('/graficas')
def graficas():
    return render_template('graficas.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)