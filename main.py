from flask import Flask, request
import psycopg2
import hashlib
from psycopg2 import sql
import sys

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


def create_database():
    conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user='postgres',
            password='Atid8431'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}")
            .format(sql.Identifier('flask_db'))
        )
    except:
        return

    cursor.close()
    conn.close()

create_database()


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
    
    conn.commit()

    cur.execute('CREATE TABLE posts (id serial PRIMARY KEY, '
                'user_id integer NOT NULL REFERENCES users (id), '
                'post_name varchar (255) NOT NULL, '
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


@app.route('/create_post', methods=["POST"])
def create_post():
    if request.method == "POST":
        user_id = request.json['user_id']
        post_name = request.json['post_name']
        content = request.json['content']

        conn = connect_db()
        cur = conn.cursor()

        cur.execute('INSERT INTO posts (user_id, post_name, content) '
                    'VALUES (%s, %s, %s)',
                    (user_id, post_name, content)
                    )
        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Post created successfully.", "error": 0}


@app.route('/get_posts', methods=["GET"])
def get_posts():
    if request.method == "GET":
        conn = connect_db()
        cur = conn.cursor()

        cur.execute('SELECT * FROM posts')
        rows = cur.fetchall()

        posts = []
        for row in rows:
            posts.append({"id": row[0], "user_id": row[1], "name": row[2], "content": row[3]})

        cur.close()
        conn.close()

        return {"posts": posts, "error": 0}


@app.route('/get_posts_by_user', methods=["GET"])
def get_posts_by_user():
    if request.method == "GET":
        app.logger.debug(request.args)
        user_id = request.args.get('user_id')

        conn = connect_db()
        cur = conn.cursor()

        cur.execute('SELECT * FROM posts WHERE user_id = %s', (user_id,))
        rows = cur.fetchall()

        posts = []
        for row in rows:
            posts.append({"id": row[0], "user_id": row[1], "name": row[2], "content": row[3]})

        cur.close()
        conn.close()

        return {"posts": posts, "error": 0}
    

@app.route('/users_count', methods=["GET"])
def get_count_users():
    if request.method == "GET":
        conn = connect_db()
        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM users')
        rows = cur.fetchall()

        # app.logger.debug(rows)
        users = 0
        for row in rows:
            users = row[0]

        cur.close()
        conn.close()

        return {"users_count": users, "error": 0}


if __name__ == '__main__':
   app.run(debug=True)