from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

CASOS_URL = os.environ.get('CASOS_URL', 'http://casos:5001')
ESTADISTICAS_URL = os.environ.get('ESTADISTICAS_URL', 'http://estadisticas:5002')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/editar')
def editar():
    return render_template('editar.html')

@app.route('/graficas')
def graficas():
    return render_template('graficas.html')

# Proxy para casos
@app.route('/api/casos', methods=['GET', 'POST'])
def casos():
    if request.method == 'GET':
        r = requests.get(f"{CASOS_URL}/api/casos")
    else:
        r = requests.post(f"{CASOS_URL}/api/casos", json=request.json)
    return jsonify(r.json()), r.status_code

@app.route('/api/casos/<int:id>', methods=['PUT', 'DELETE'])
def caso(id):
    if request.method == 'PUT':
        r = requests.put(f"{CASOS_URL}/api/casos/{id}", json=request.json)
    else:
        r = requests.delete(f"{CASOS_URL}/api/casos/{id}")
    return jsonify(r.json()), r.status_code

# Proxy para estadisticas
@app.route('/api/estadisticas')
def estadisticas():
    r = requests.get(f"{ESTADISTICAS_URL}/api/estadisticas")
    return jsonify(r.json())

@app.route('/api/datos-enfermedades')
def enfermedades():
    r = requests.get(f"{ESTADISTICAS_URL}/api/datos-enfermedades")
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)