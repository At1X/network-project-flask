from flask import Flask, request
import psycopg2
import hashlib


app = Flask(__name__)


def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def verify_password(input_password, stored_password):
    hashed_input_password = hashlib.sha256(input_password.encode()).hexdigest()
    return hashed_input_password == stored_password


def connect_db():
    conn = psycopg2.connect(
            host="localhost",
            database="flask_db",
            user='postgres',
            password='Atid8431'
    )
    return conn



def table_exists(table_name):
    """Checks if the specified table exists in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists


if not table_exists('users') and not table_exists('posts'):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('CREATE TABLE users (id serial PRIMARY KEY, '
                'username varchar (255) NOT NULL, '
                'email varchar (255) NOT NULL, '
                'password varchar NOT NULL)'
                )
    
    cur.execute('CREATE TABLE posts (id serial PRIMARY KEY, '
                'user_id integer NOT NULL REFERENCES users (id), '
                'content text NOT NULL);'
                )
    
    conn.commit()
    cur.close()
    conn.close()



@app.route('/register', methods=["POST",])
def register():
       if request.method == "POST":
            username = request.json['username']
            email = request.json['email']
            password = request.json['password']

            hashed_password = hash_password(password)

            conn = connect_db()
            cur = conn.cursor()

            cur.execute('INSERT INTO users (username, email, password) '
                        'VALUES (%s, %s, %s)',
                        (username, email, hashed_password)
                        )
            conn.commit()
            cur.close()
            conn.close()

            return {"message": f"User %{username} registered successfully.", "error": 0}


@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        username = request.json['username']
        password = request.json['password']

        conn = connect_db()
        cur = conn.cursor()

        cur.execute('SELECT password FROM users WHERE username = %s', (username,))
        row = cur.fetchone()

        if row:
            stored_password = row[0]
            if verify_password(password, stored_password):
                cur.close()
                conn.close()
                return {"message": "Login successful.", "error": 0}
            else:
                cur.close()
                conn.close()
                return {"message": "Invalid username or password.", "error": 1}
        else:
            cur.close()
            conn.close()
            return {"message": "Invalid username or password.", "error": 1}





if __name__ == '__main__':
   app.run(debug=True)