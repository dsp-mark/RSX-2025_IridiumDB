from flask import Flask, request, jsonify, render_template
import sqlite3 as sqlite

app = Flask(__name__)

def init_db():
    print("Running Init DB; make sure the db was created")
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



@app.route("/raw_iridium", methods=["GET","POST"])
def raw_data():
    conn = sqlite.connect('rsx.db')
    c = conn.cursor()
    
    if request.method == "POST":
        data = request.get_json()
        content = data.get("message")

        if not content:
            return jsonify({'error': 'No message provided'}), 400
        
        c.execute('''
                INSERT INTO raw_data (message) VALUES (?)
                ''', (content,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Message stored'}), 200
    elif request.method == "GET":
        c.execute('''
                  SELECT id, message FROM raw_data;
                  ''')
        rows = c.fetchall()
        conn.close()
        messages = [{"id": row[0], "message": row[1]} 
        for row in rows]
        return jsonify(messages), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)