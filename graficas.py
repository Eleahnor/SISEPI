# graficas_service.py - Microservicio para gráficas epidemiológicas
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import date

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISEPI - Dashboard de Enfermedades</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #2E7D32;
            font-size: 28px;
        }
        .header p {
            color: #666;
            margin-top: 5px;
        }
        .graficas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .grafica-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .grafica-card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
            border-left: 4px solid #2E7D32;
            padding-left: 10px;
        }
        .grafica-container {
            width: 100%;
            height: 450px;
        }
        .stats-resumen {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-card {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #2E7D32;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .btn-actualizar {
            background: #2E7D32;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 14px;
        }
        .btn-actualizar:hover {
            background: #1B5E20;
        }
        @media (max-width: 768px) {
            .graficas-grid {
                grid-template-columns: 1fr;
            }
            .grafica-container {
                height: 350px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 SISEPI - Dashboard Epidemiológico</h1>
            <p>Análisis de enfermedades en Baja California Sur</p>
            <button class="btn-actualizar" onclick="actualizarGraficas()">🔄 Actualizar Datos</button>
        </div>

        <div class="graficas-grid">
            <!-- Gráfica de Pastel -->
            <div class="grafica-card">
                <h2>🥧 Distribución de Enfermedades</h2>
                <div id="graficaPastel" class="grafica-container"></div>
            </div>

            <!-- Gráfica de Barras -->
            <div class="grafica-card">
                <h2>📊 Casos por Enfermedad</h2>
                <div id="graficaBarras" class="grafica-container"></div>
            </div>
        </div>

        <div class="stats-resumen">
            <h2>📈 Resumen Epidemiológico</h2>
            <div class="stats-grid" id="resumenStats">
                <p>Cargando estadísticas...</p>
            </div>
        </div>
    </div>

    <script>
        const API_URL = 'http://localhost:5004/api';
        
        async function cargarDatos() {
            try {
                const response = await fetch(`${API_URL}/datos-enfermedades`);
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error cargando datos:', error);
                return null;
            }
        }
        
        async function actualizarGraficas() {
            const datos = await cargarDatos();
            if (!datos) {
                alert('Error al cargar los datos');
                return;
            }
            
            // Gráfica de Pastel
            const pieTrace = {
                values: datos.porcentajes,
                labels: datos.enfermedades,
                type: 'pie',
                marker: {
                    colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
                    line: { color: 'white', width: 2 }
                },
                textinfo: 'label+percent',
                textposition: 'auto',
                hole: 0.3,
                hoverinfo: 'label+percent+value'
            };
            
            const pieLayout = {
                title: {
                    text: 'Distribución de Casos por Enfermedad',
                    font: { size: 16, family: 'Arial' }
                },
                showlegend: true,
                legend: { orientation: 'h', y: -0.1 }
            };
            
            Plotly.newPlot('graficaPastel', [pieTrace], pieLayout);
            
            // Gráfica de Barras
            const barTrace = {
                x: datos.enfermedades,
                y: datos.cantidades,
                type: 'bar',
                marker: {
                    color: '#4ECDC4',
                    line: { color: '#2E7D32', width: 1.5 }
                },
                text: datos.cantidades,
                textposition: 'auto',
                hoverinfo: 'x+y'
            };
            
            const barLayout = {
                title: {
                    text: 'Número de Casos por Enfermedad',
                    font: { size: 16, family: 'Arial' }
                },
                xaxis: {
                    title: 'Enfermedad',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Número de Casos',
                    gridcolor: '#e0e0e0'
                },
                bargap: 0.3
            };
            
            Plotly.newPlot('graficaBarras', [barTrace], barLayout);
            
            // Actualizar resumen
            const statsDiv = document.getElementById('resumenStats');
            statsDiv.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${datos.total_casos}</div>
                    <div class="stat-label">Total de Casos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${datos.enfermedades.length}</div>
                    <div class="stat-label">Enfermedades Registradas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${datos.enfermedad_mas_comun?.nombre || 'N/A'}</div>
                    <div class="stat-label">Enfermedad más común</div>
                    <small>${datos.enfermedad_mas_comun?.casos || 0} casos</small>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${Math.max(...datos.porcentajes, 0)}%</div>
                    <div class="stat-label">Mayor porcentaje</div>
                </div>
            `;
        }
        
        // Cargar gráficas al iniciar
        actualizarGraficas();
        
        // Actualizar cada 30 segundos
        setInterval(actualizarGraficas, 30000);
    </script>
</body>
</html>
'''

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