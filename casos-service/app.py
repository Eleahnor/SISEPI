from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
from collections import Counter
import os

app = Flask(__name__)
CORS(app)

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
    diag_date = db.Column(db.Date, default=date.today)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'edad': self.edad,
            'sexo': self.sexo,
            'municipio': self.municipio,
            'enfermedad': self.enfermedad,
            'tipo': self.tipo,
            'estado': self.estado,
            'diag_date': self.diag_date.isoformat() if self.diag_date else None
        }

MUNICIPIOS_BCS = ['La Paz', 'Los Cabos', 'Comondú', 'Mulegé', 'Loreto']

@app.before_first_request
def init_db():
    db.create_all()
    if Caso.query.count() == 0:
        ejemplos = [
            Caso(nombre='Juan Pérez', edad=45, sexo='M', municipio='La Paz', 
                 enfermedad='Dengue', tipo='Confirmado', estado='Activo'),
            Caso(nombre='María López', edad=32, sexo='F', municipio='Los Cabos', 
                 enfermedad='COVID-19', tipo='Sospechoso', estado='Activo'),
            Caso(nombre='Carlos Ruiz', edad=58, sexo='M', municipio='Comondú', 
                 enfermedad='Zika', tipo='Confirmado', estado='Recuperado'),
            Caso(nombre='Ana García', edad=27, sexo='F', municipio='La Paz', 
                 enfermedad='Dengue', tipo='Descartado', estado='Recuperado'),
            Caso(nombre='Roberto Soto', edad=63, sexo='M', municipio='Mulegé', 
                 enfermedad='COVID-19', tipo='Confirmado', estado='Fallecido'),
            Caso(nombre='Laura Méndez', edad=41, sexo='F', municipio='Loreto', 
                 enfermedad='Chikungunya', tipo='Confirmado', estado='Activo'),
        ]
        db.session.add_all(ejemplos)
        db.session.commit()

@app.route('/api/casos', methods=['GET'])
def get_casos():
    municipio = request.args.get('municipio')
    tipo = request.args.get('tipo')
    
    query = Caso.query
    if municipio:
        query = query.filter_by(municipio=municipio)
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    casos = query.all()
    return jsonify([c.to_dict() for c in casos])

@app.route('/api/casos/<int:id>', methods=['GET'])
def get_caso(id):
    caso = Caso.query.get_or_404(id)
    return jsonify(caso.to_dict())

@app.route('/api/casos', methods=['POST'])
def create_caso():
    data = request.json
    
    if data['municipio'] not in MUNICIPIOS_BCS:
        return jsonify({'error': 'Municipio no válido'}), 400
    if not data.get('enfermedad'):
        return jsonify({'error': 'La enfermedad es requerida'}), 400
    
    nuevo_caso = Caso(
        nombre=data.get('nombre', 'Anónimo'),
        edad=data['edad'],
        sexo=data['sexo'],
        municipio=data['municipio'],
        enfermedad=data.get('enfermedad', 'Desconocida'),
        tipo=data.get('tipo', 'Sospechoso'),
        estado=data.get('estado', 'Activo')
    )
    
    db.session.add(nuevo_caso)
    db.session.commit()
    return jsonify(nuevo_caso.to_dict()), 201

@app.route('/api/casos/<int:id>', methods=['PUT'])
def update_caso(id):
    caso = Caso.query.get_or_404(id)
    data = request.json
    
    if 'nombre' in data: caso.nombre = data['nombre']
    if 'edad' in data: caso.edad = data['edad']
    if 'sexo' in data: caso.sexo = data['sexo']
    if 'municipio' in data: caso.municipio = data['municipio']
    if 'enfermedad' in data: caso.enfermedad = data['enfermedad']
    if 'tipo' in data: caso.tipo = data['tipo']
    if 'estado' in data: 
        if caso.estado == 'Fallecido':
            return jsonify({'error': 'El estado fallecido no se puede cambiar'}), 400
        caso.estado = data['estado']
    
    db.session.commit()
    return jsonify(caso.to_dict())

@app.route('/api/casos/<int:id>', methods=['DELETE'])
def delete_caso(id):
    caso = Caso.query.get_or_404(id)
    db.session.delete(caso)
    db.session.commit()
    return jsonify({'message': 'Caso eliminado'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)