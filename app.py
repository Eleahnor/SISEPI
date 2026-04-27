from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
from collections import Counter
import json

app = Flask(__name__)
CORS(app)  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisepi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# mod case
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

# grax depy
with app.app_context():
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


MUNICIPIOS_BCS = ['La Paz', 'Los Cabos', 'Comondú', 'Mulegé', 'Loreto']




# endpoints para la API

# s1 - CRUD
@app.route('/api/casos', methods=['GET'])
def get_casos():
    #obtiene casos o filtra
    municipio = request.args.get('municipio')
    tipo = request.args.get('tipo')
    
    query = Caso.query
    if municipio:
        query = query.filter_by(municipio=municipio)
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    casos = query.all()
    return jsonify([c.to_dict() for c in casos])

@app.route('/api/casos', methods=['POST'])
def create_caso():
    #crear caso
    data = request.json
    
    if data['municipio'] not in MUNICIPIOS_BCS:
        return jsonify({'error': 'Municipio no válido'}), 400
    
    nuevo_caso = Caso(
        edad=data['edad'],
        sexo=data['sexo'],
        municipio=data['municipio'],
        tipo=data.get('tipo', 'Sospechoso'),
        estado=data.get('estado', 'Activo')
    )
    db.session.add(nuevo_caso)
    db.session.commit()
    return jsonify(nuevo_caso.to_dict()), 201

@app.route('/api/casos/<int:id>', methods=['PUT'])
def update_caso(id):
    #modificar
    caso = Caso.query.get_or_404(id)
    data = request.json
    
    if 'edad' in data: caso.edad = data['edad']
    if 'sexo' in data: caso.sexo = data['sexo']
    if 'municipio' in data: caso.municipio = data['municipio']
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

# s2 - municipios
# @app.route('/api/municipios', methods=['GET'])
# def get_municipios():
#     return jsonify(MUNICIPIOS_BCS)

@app.route('/api/municipios/<nombre>/estadisticas', methods=['GET'])
def get_municipio_stats(nombre):
    if nombre not in MUNICIPIOS_BCS:
        return jsonify({'error': 'Municipio no encontrado'}), 404
    
    casos = Caso.query.filter_by(municipio=nombre).all()
    return jsonify({
        'municipio': nombre,
        'total_casos': len(casos),
        'confirmados': sum(1 for c in casos if c.tipo == 'Confirmado'),
        'activos': sum(1 for c in casos if c.estado == 'Activo'),
        'recuperados': sum(1 for c in casos if c.estado == 'Recuperado')
    })


@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    todos = Caso.query.all()
    
    if not todos:
        return jsonify({'total': 0})
    
    edades = [c.edad for c in todos]
    
    return jsonify({
        'total_casos': len(todos),
        'promedio_edad': round(sum(edades) / len(edades), 1),
        'por_municipio': dict(Counter(c.municipio for c in todos)),
        'por_tipo': dict(Counter(c.tipo for c in todos)),
        'por_estado': dict(Counter(c.estado for c in todos)),
        'municipios': MUNICIPIOS_BCS
    })

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


# ruta principal para servir la PWA
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)