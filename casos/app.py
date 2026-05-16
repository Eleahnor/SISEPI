from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import date
import json

app = Flask(__name__)
CORS(app)

DB_PATH = '/data/sisepi.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad INTEGER,
            sexo TEXT,
            municipio TEXT,
            enfermedad TEXT,
            tipo TEXT,
            estado TEXT,
            diag_date TEXT
        )
    ''')
    
    # Datos de ejemplo
    cursor.execute("SELECT COUNT(*) FROM casos")
    if cursor.fetchone()[0] == 0:
        ejemplos = [
            ('Juan Pérez', 45, 'M', 'La Paz', 'Dengue', 'Confirmado', 'Activo', date.today().isoformat()),
            ('María López', 32, 'F', 'Los Cabos', 'COVID-19', 'Sospechoso', 'Activo', date.today().isoformat()),
            ('Carlos Ruiz', 58, 'M', 'Comondú', 'Zika', 'Confirmado', 'Recuperado', date.today().isoformat()),
            ('Ana García', 27, 'F', 'La Paz', 'Dengue', 'Descartado', 'Recuperado', date.today().isoformat()),
            ('Roberto Soto', 63, 'M', 'Mulegé', 'COVID-19', 'Confirmado', 'Fallecido', date.today().isoformat()),
            ('Laura Méndez', 41, 'F', 'Loreto', 'Chikungunya', 'Confirmado', 'Activo', date.today().isoformat()),
        ]
        cursor.executemany("INSERT INTO casos (nombre, edad, sexo, municipio, enfermedad, tipo, estado, diag_date) VALUES (?,?,?,?,?,?,?,?)", ejemplos)
        conn.commit()
    
    conn.close()

@app.route('/health')
def health():
    return {'status': 'ok'}

@app.route('/api/casos', methods=['GET'])
def get_casos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM casos ORDER BY id DESC")
    casos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(casos)

@app.route('/api/casos', methods=['POST'])
def create_caso():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO casos (nombre, edad, sexo, municipio, enfermedad, tipo, estado, diag_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('nombre', 'Anónimo'),
        data.get('edad', 0),
        data.get('sexo', ''),
        data['municipio'],
        data['enfermedad'],
        data.get('tipo', 'Sospechoso'),
        data.get('estado', 'Activo'),
        date.today().isoformat()
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'message': 'Caso creado'}), 201

@app.route('/api/casos/<int:id>', methods=['PUT'])
def update_caso(id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE casos 
        SET nombre=?, edad=?, sexo=?, municipio=?, enfermedad=?, tipo=?, estado=?
        WHERE id=?
    """, (
        data.get('nombre'),
        data.get('edad'),
        data.get('sexo'),
        data.get('municipio'),
        data.get('enfermedad'),
        data.get('tipo'),
        data.get('estado'),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caso actualizado'})

@app.route('/api/casos/<int:id>', methods=['DELETE'])
def delete_caso(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM casos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Caso eliminado'})

# Inicializar DB
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)