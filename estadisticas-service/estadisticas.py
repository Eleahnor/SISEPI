from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
import os
import redis
import json
from datetime import datetime

app = Flask(__name__)

# Configuración de base de datos
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'sisepi')
db_password = os.environ.get('DB_PASSWORD', 'sisepi123')
db_name = os.environ.get('DB_NAME', 'sisepi')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Caso(db.Model):
    __tablename__ = 'casos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    sexo = db.Column(db.String(10))
    municipio = db.Column(db.String(50))
    enfermedad = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    estado = db.Column(db.String(20))
    diag_date = db.Column(db.Date)

MUNICIPIOS_BCS = ['La Paz', 'Los Cabos', 'Comondú', 'Mulegé', 'Loreto']

# Configuración de Redis
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
CACHE_TIMEOUT = 300  # 5 minutos

@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    # Verificar cache
    cache_key = 'estadisticas_generales'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    todos = Caso.query.all()
    
    if not todos:
        result = {'total': 0}
    else:
        edades = [c.edad for c in todos]
        result = {
            'total_casos': len(todos),
            'promedio_edad': round(sum(edades) / len(edades), 1),
            'por_municipio': dict(Counter(c.municipio for c in todos)),
            'por_tipo': dict(Counter(c.tipo for c in todos)),
            'por_estado': dict(Counter(c.estado for c in todos)),
            'por_enfermedad': dict(Counter(c.enfermedad for c in todos if c.enfermedad)),
            'municipios': MUNICIPIOS_BCS
        }
    
    # Guardar en cache
    redis_client.setex(cache_key, CACHE_TIMEOUT, json.dumps(result))
    
    return jsonify(result)

@app.route('/api/municipios/<nombre>/estadisticas', methods=['GET'])
def get_municipio_stats(nombre):
    if nombre not in MUNICIPIOS_BCS:
        return jsonify({'error': 'Municipio no encontrado'}), 404
    
    cache_key = f'estadisticas_municipio_{nombre}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    casos = Caso.query.filter_by(municipio=nombre).all()
    result = {
        'municipio': nombre,
        'total_casos': len(casos),
        'confirmados': sum(1 for c in casos if c.tipo == 'Confirmado'),
        'activos': sum(1 for c in casos if c.estado == 'Activo'),
        'recuperados': sum(1 for c in casos if c.estado == 'Recuperado')
    }
    
    redis_client.setex(cache_key, CACHE_TIMEOUT, json.dumps(result))
    
    return jsonify(result)

@app.route('/api/tendencia', methods=['GET'])
def get_tendencia():
    stats = {}
    for municipio in MUNICIPIOS_BCS:
        casos = Caso.query.filter_by(municipio=municipio).all()
        stats[municipio] = {
            'total': len(casos),
            'confirmados': sum(1 for c in casos if c.tipo == 'Confirmado')
        }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5002)