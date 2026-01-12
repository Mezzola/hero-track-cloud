# server.py - Servidor Cloud Hero Track (PythonAnywhere)
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Dados em memória
latest_data = {}
API_KEY = "hero-track-secret-2025"

# Dashboard HTML SIMPLES
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚣 Hero Track - Tempo Real</title>
    <style>
        body { font-family: Arial; background: #0f172a; color: white; padding: 20px; }
        .header { text-align: center; padding: 20px; background: #1e293b; border-radius: 10px; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 10px; }
        .paddle { background: #334155; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .online { border-left: 5px solid #10b981; }
        .offline { border-left: 5px solid #ef4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚣 Hero Track - Monitoramento</h1>
        <p>Acesso Global em Tempo Real</p>
        <p id="status">🟡 Conectando...</p>
    </div>
    
    <div class="cards">
        <div class="card">
            <h3>📍 Posição GPS</h3>
            <p>Latitude: <span id="lat">--</span></p>
            <p>Longitude: <span id="lon">--</span></p>
            <p>Velocidade: <span id="speed">--</span> m/s</p>
            <p>Satélites: <span id="sats">--</span></p>
        </div>
        
        <div class="card">
            <h3>🚣 Status dos Remos</h3>
            <div id="paddles">
                <!-- Preenchido por JavaScript -->
            </div>
        </div>
        
        <div class="card">
            <h3>📊 Sistema</h3>
            <p>Última atualização: <span id="lastUpdate">--:--:--</span></p>
            <p>Pacotes recebidos: <span id="packets">0</span></p>
            <p>Servidor: <span id="serverTime">--:--:--</span></p>
        </div>
    </div>
    
    <script>
        async function updateData() {
            try {
                const response = await fetch('/api/latest');
                const data = await response.json();
                
                if (data.status === 'success') {
                    document.getElementById('status').innerHTML = '🟢 Online';
                    
                    // GPS
                    const boat = data.data.boat;
                    if (boat && boat.gps_valid) {
                        document.getElementById('lat').textContent = boat.lat.toFixed(6);
                        document.getElementById('lon').textContent = boat.lon.toFixed(6);
                        document.getElementById('speed').textContent = boat.speed.toFixed(2);
                        document.getElementById('sats').textContent = boat.satellites;
                    }
                    
                    // Remos
                    const paddles = data.data.paddles || [];
                    let html = '';
                    paddles.forEach(p => {
                        html += `
                            <div class="paddle ${p.connected ? 'online' : 'offline'}">
                                <strong>Remo ${p.id}</strong><br>
                                ❤️ ${p.connected ? p.heart_rate.toFixed(0) + ' BPM' : '--'}<br>
                                💪 ${p.connected ? p.force_n.toFixed(0) + ' N' : '--'}<br>
                                🔋 ${p.connected ? p.battery_percent + '%' : '--'}
                            </div>
                        `;
                    });
                    document.getElementById('paddles').innerHTML = html;
                    
                    // Sistema
                    document.getElementById('lastUpdate').textContent = 
                        new Date().toLocaleTimeString();
                    document.getElementById('packets').textContent = 
                        data.data.system?.packets_total || 0;
                }
            } catch (error) {
                console.error(error);
                document.getElementById('status').innerHTML = '🔴 Erro conexão';
            }
        }
        
        // Atualizar a cada 2 segundos
        setInterval(updateData, 2000);
        updateData();
        
        // Atualizar hora do servidor
        setInterval(() => {
            document.getElementById('serverTime').textContent = 
                new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML

@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'status': 'error', 'message': 'API key inválida'}), 401
        
        data = request.get_json()
        data['received_at'] = datetime.now().isoformat()
        
        # Armazenar
        global latest_data
        latest_data = data
        
        print(f"✅ Dados recebidos de {data.get('device_id', 'desconhecido')}")
        return jsonify({'status': 'success', 'message': 'OK'})
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/latest', methods=['GET'])
def get_latest():
    if latest_data:
        return jsonify({
            'status': 'success',
            'data': latest_data
        })
    else:
        return jsonify({
            'status': 'success',
            'data': {
                'boat': {'gps_valid': False},
                'paddles': [],
                'system': {}
            }
        })

@app.route('/health')
def health():
    return jsonify({
        'status': 'online',
        'service': 'Hero Track Cloud',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
