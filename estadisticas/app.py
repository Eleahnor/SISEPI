from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
from collections import Counter

app = Flask(__name__)
CORS(app)

DB_PATH = '/data/sisepi.db'

@app.route('/health')
def health():
    return {'status': 'ok'}

@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos")
    casos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not casos:
        return jsonify({'total': 0})
    
    edades = [c['edad'] for c in casos if c['edad']]
    
    return jsonify({
        'total_casos': len(casos),
        'promedio_edad': round(sum(edades) / len(edades), 1) if edades else 0,
        'por_municipio': dict(Counter(c['municipio'] for c in casos)),
        'por_tipo': dict(Counter(c['tipo'] for c in casos)),
        'por_estado': dict(Counter(c['estado'] for c in casos)),
        'por_enfermedad': dict(Counter(c['enfermedad'] for c in casos))
    })

@app.route('/api/datos-enfermedades', methods=['GET'])
def enfermedades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT enfermedad, COUNT(*) as total FROM casos GROUP BY enfermedad")
    resultados = cursor.fetchall()
    conn.close()
    
    enfermedades = [r[0] for r in resultados]
    cantidades = [r[1] for r in resultados]
    
    return jsonify({
        'enfermedades': enfermedades,
        'cantidades': cantidades,
        'total_casos': sum(cantidades)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)