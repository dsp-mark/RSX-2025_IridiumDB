from flask import Flask, request, jsonify, render_template, url_for
import sqlite3 as sqlite

app = Flask(__name__)

def db_run(SQL_CODE):
    try:
        conn = sqlite.connect('rsx.db')
        c = conn.cursor()
        c.execute(SQL_CODE)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)

def db_fetch(SQL_CODE):
    try:
        conn = sqlite.connect('rsx.db')
        c = conn.cursor()
        c.execute(SQL_CODE)
        query_results = c.fetchall()
        conn.commit()
        conn.close()

        return query_results
    except Exception as e:
        print(e)


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
    raw_messages = db_fetch('''
             SELECT id, message, received_at FROM raw_data;
             ''')
    return render_template("index.html", raw_messages=raw_messages)



@app.route("/raw_iridium", methods=["GET","POST"])
def raw_data():
    if request.method == "POST":
        data = request.get_json()
        message_to_add = data.get("message")

        if not message_to_add:
            return jsonify({'error': 'No message provided'}), 400
        
        db_run(f'''
                INSERT INTO raw_data (message) VALUES ("{message_to_add}")
                ''')
        
        return jsonify({'status': 'Message stored'}), 200
    
    elif request.method == "GET":
        raw_messages = db_fetch('''
                                SELECT id, message, received_at FROM raw_data;
                                ''')

        messages = [{"id": msg[0], "message": msg[1], "received_at": msg[2]} 
        for msg in raw_messages]
        return jsonify(messages), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)