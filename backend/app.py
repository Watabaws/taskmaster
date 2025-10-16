import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
# Enable CORS for all routes (necessary for frontend/backend communication)
CORS(app)

# --- Database Connection Setup ---
def get_db_connection():
    # Use environment variables set by Kubernetes for the PostgreSQL Service
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres-service"), # Use the K8s Service name
        database=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "password")
    )
    return conn

# --- Database Initialization (Runs once on startup attempt) ---
def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Create the tasks table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        # NOTE: In a K8s loop, this often fails initially until Postgres is ready.
        print(f"Database connection or initialization failed: {e}")
    finally:
        if conn:
            conn.close()

# Initialize database on app startup
init_db()

# --- API Routes ---

# ROUTE 1: GET /tasks (Fetch all tasks) and POST /tasks (Create new task)
@app.route('/tasks', methods=['GET', 'POST'])
def tasks_route():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Handle GET request to fetch all tasks
        if request.method == 'GET':
            cur.execute("SELECT id, title, completed FROM tasks ORDER BY id DESC")
            tasks = cur.fetchall()

            # Format results into a list of dictionaries
            task_list = [
                {"id": task[0], "title": task[1], "completed": task[2]}
                for task in tasks
            ]
            return jsonify(task_list)

        # Handle POST request to create a new task
        elif request.method == 'POST':
            data = request.get_json()
            title = data.get('title')

            if not title:
                return jsonify({"error": "Title is required"}), 400

            cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id;", (title,))
            new_id = cur.fetchone()[0]
            conn.commit()

            return jsonify({"id": new_id, "title": title, "completed": False}), 201

    except psycopg2.OperationalError as e:
        # Specific error for connection failure (e.g., Postgres not ready)
        return jsonify({"error": "Database connection failed", "details": str(e)}), 503
    except Exception as e:
        # General exception handling
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn:
            conn.close()

# ROUTE 2: PUT /tasks/<int:task_id> (Update task status)
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task_route(task_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        data = request.get_json()
        completed = data.get('completed', False) # Default to False if not present

        cur.execute("UPDATE tasks SET completed = %s WHERE id = %s RETURNING id;",
                    (completed, task_id))

        if cur.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        conn.commit()
        return jsonify({"message": "Task updated successfully"}), 200

    except psycopg2.OperationalError as e:
        return jsonify({"error": "Database connection failed", "details": str(e)}), 503
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # This block is typically only used for local debugging, Gunicorn handles production
    app.run(host='0.0.0.0', port=5000)
