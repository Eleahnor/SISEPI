# graficas_service.py - Microservicio para gráficas epidemiológicas
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import date

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = """"""
def get_db_connection():
    conn = sqlite3.connect('instance/sisepi.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/datos-enfermedades', methods=['GET'])
def get_datos_enfermedades():
    conn = get_db_connection()
    
    # Consultar casos agrupados por enfermedad
    cursor = conn.execute('''
        SELECT enfermedad, COUNT(*) as total 
        FROM casos 
        WHERE enfermedad IS NOT NULL AND enfermedad != ''
        GROUP BY enfermedad 
        ORDER BY total DESC
    ''')
    
    resultados = cursor.fetchall()
    conn.close()
    
    if not resultados:
        return jsonify({
            'enfermedades': ['Sin datos'],
            'cantidades': [0],
            'porcentajes': [100],
            'total_casos': 0,
            'enfermedad_mas_comun': None
        })
    
    enfermedades = [row['enfermedad'] for row in resultados]
    cantidades = [row['total'] for row in resultados]
    total = sum(cantidades)
    porcentajes = [round((c/total)*100, 1) for c in cantidades]
    
    # Encontrar enfermedad más común
    idx_max = cantidades.index(max(cantidades))
    
    return jsonify({
        'enfermedades': enfermedades,
        'cantidades': cantidades,
        'porcentajes': porcentajes,
        'total_casos': total,
        'enfermedad_mas_comun': {
            'nombre': enfermedades[idx_max],
            'casos': cantidades[idx_max],
            'porcentaje': porcentajes[idx_max]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)