from flask import Flask, render_template, jsonify, request
import mysql.connector
from datetime import datetime
import time

app = Flask(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'gymenergy',
    'password': 'strongpassword',
    'database': 'gym_energy'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.form
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO energy_data 
            (voltage, current, power, energy, emergency_power) 
            VALUES (%s, %s, %s, %s, %s)""",
            (float(data['voltage']), 
             float(data['current']),
             float(data['power']),
             float(data['energy']),
             int(data['emergency']))
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Data stored successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/data')
def get_latest_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM energy_data ORDER BY timestamp DESC LIMIT 1")
        latest = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                SUM(energy) as total_energy,
                AVG(power) as avg_power,
                MAX(timestamp) as last_update 
            FROM energy_data 
            WHERE timestamp >= NOW() - INTERVAL 1 DAY
        """)
        summary = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'latest': latest,
            'summary': summary,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)