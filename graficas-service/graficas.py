from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

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
    enfermedad = db.Column(db.String(50))

@app.route('/api/datos-enfermedades', methods=['GET'])
def get_datos_enfermedades():
    resultados = db.session.query(
        Caso.enfermedad, 
        func.count(Caso.id).label('total')
    ).filter(Caso.enfermedad != '', Caso.enfermedad.isnot(None)).group_by(Caso.enfermedad).order_by(func.count(Caso.id).desc()).all()
    
    if not resultados:
        return jsonify({
            'enfermedades': ['Sin datos'],
            'cantidades': [0],
            'porcentajes': [100],
            'total_casos': 0,
            'enfermedad_mas_comun': None
        })
    
    enfermedades = [r[0] for r in resultados]
    cantidades = [r[1] for r in resultados]
    total = sum(cantidades)
    porcentajes = [round((c/total)*100, 1) for c in cantidades]
    
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
    app.run(debug=False, host='0.0.0.0', port=5003)