from flask import Flask, request, jsonify, render_template
import sqlite3 as sqlite
import msgpack
import json

app = Flask(__name__)

def db_run(SQL_CODE, params=None):
    try:
        conn = sqlite.connect('rsx.db')
        c = conn.cursor()
        if params:
            c.execute(SQL_CODE, params)
        else:
            c.execute(SQL_CODE)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)

def db_fetch(SQL_CODE, params=None):
    try:
        conn = sqlite.connect('rsx.db')
        c = conn.cursor()
        if params:
            c.execute(SQL_CODE, params)
        else:
            c.execute(SQL_CODE)
        query_results = c.fetchall()
        conn.commit()
        conn.close()
        return query_results
    except Exception as e:
        print(e)
        return []

def init_db():
    db_run('''
        CREATE TABLE IF NOT EXISTS raw_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        received_at DATETIME NOT NULL DEFAULT(datetime('now','localtime'))  
        );
        ''')

@app.route("/")
def index():
    raw_messages = db_fetch('SELECT id, message, received_at FROM raw_data;')
    return render_template("index.html", raw_messages=raw_messages)

@app.route("/raw_iridium", methods=["GET","POST"])
def raw_data():
    if request.method == "POST":
        data = request.get_json()
        print("DATA:", data)
        hex_message = data.get("data")

        if not hex_message:
            return jsonify({"error":"No message found"}), 400
        
        try:
            decoded_bytes = bytes.fromhex(hex_message)
            decoded_message = msgpack.unpackb(decoded_bytes)
            print("DECODED 1: ", decoded_bytes)
            print("DECODED 2: ", decoded_message)
        except Exception as e:
            return jsonify({"error": f'Failed to decode: {e}'}), 400

        db_run("INSERT INTO raw_data (message) VALUES (?)", (json.dumps(decoded_message),))

        return jsonify({'status': 'Message stored'}), 200
    
    elif request.method == "GET":
        raw_messages = db_fetch('SELECT id, message, received_at FROM raw_data;')
        messages = [
            {
                "id": msg[0],
                "message": json.loads(msg[1]),
                "received_at": msg[2]
            }
            for msg in raw_messages
        ]
        return jsonify(messages), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
