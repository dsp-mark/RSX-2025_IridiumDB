from flask import Flask, request, jsonify, render_template
import sqlite3 as sqlite

app = Flask(__name__)

def init_db():
    conn = sqlite.connect('rsx.db')
    c = conn.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL  
                );
              ''')
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/raw_iridium", methods=["POST"])
def receive_iridium():
    data = request.get_json()
    content = data.get("message")

    if not content:
        return jsonify({'error': 'No message provided'}), 400
    
    conn = sqlite.connect('rsx.db')
    c = conn.cursor()
    c.execute('''
              INSERT INTO raw_data (content) VALUES (?)
              ''', (content,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Message stored'}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)