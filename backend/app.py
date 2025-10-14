import os
import json
import psycopg2
from flask import Flask, jsonify, request, after_request
from contextlib import contextmanager

app = Flask(__name__)

DB_NAME = os.environ.get('POSTGRES_DB', 'tasks')
DB_USER = os.environ.get('POSTGRES_USER', 'todo_user')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'supersecret')
DB_HOST = os.environ.get('POSTGRES_SERVICE_HOST', 'postgres-service')
DB_PORT = os.environ.get('POSTGRES_SERVICE_PORT', '5432')

@contextmanager
def get_db_cursor(commit=False):
    """Provides a database cursor and handles connection/cursor closing."""
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        yield cursor

        if commit:
            conn.commit()

    except Exception as error:
        print(f"Database error: {error}")
        # 4. Rollback changes on error
        if conn:
            conn.rollback()
        # Raise the error so the API endpoint can return a 500 status
        raise

    finally:
        # 5. Ensure resources are always released
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_db():
    print("Attempting to initialize database...")
    # How do we call our new helper to get a cursor and ensure the changes are saved?
    with get_db_cursor(commit=True) as cur:
        # SQL to create the table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL
            );
        """)
        print("Database table ensured.")

        cur.execute("SELECT count(*) FROM tasks;")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO tasks (title) VALUES ('Containerize backend'), ('Deploy to Minikube');")
            print("Initial tasks inserted.")

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    with get_db_cursor() as cur:
        cur.execute("SELECT id, title FROM tasks ORDER BY id;")
        results = cur.fetchall()

    tasks = [{'id': row[0], 'title': row[1]} for row in results]

    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Inserts a new task into the database."""
    data = request.json
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        # DML operation: commit=True is required
        with get_db_cursor(commit=True) as cur:
            # We use a parameterized query (title=%s) to prevent SQL Injection.
            # RETURNING id is used to get the auto-generated primary key back.
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id;",
                (title,) # <-- The data is passed as a separate tuple
            )
            # Fetch the returned ID
            new_id = cur.fetchone()[0]

        # Return the newly created task object to the client
        return jsonify({'id': new_id, 'title': title}), 201

    except Exception as e:
        print(f"POST /api/tasks failed: {e}")
        return jsonify({'error': 'Failed to save task to database'}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

