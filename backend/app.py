import os
import time
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# Database configuration & helpers
# -----------------------------------------------------------------------------
DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres-service"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "tasks"),
    "user": os.getenv("POSTGRES_USER", "todo_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "supersecret"),
    "connect_timeout": int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "5")),
}

TABLE_DEFINITION = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

DEFAULT_SEED_TASKS = [
    "Welcome to the Kubernetes ToDo demo!",
    "Deploy the backend API",
    "Connect the frontend via the /api proxy",
]

SEED_TASKS_ENV = os.getenv("SEED_TASKS")
SEED_TASKS = (
    [task.strip() for task in SEED_TASKS_ENV.split(",") if task.strip()]
    if SEED_TASKS_ENV
    else DEFAULT_SEED_TASKS
)

INIT_RETRY_ATTEMPTS = int(os.getenv("DB_INIT_ATTEMPTS", "12"))
INIT_RETRY_DELAY = int(os.getenv("DB_INIT_DELAY_SECONDS", "5"))


@contextmanager
def db_connection():
    """Provide a managed database connection."""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Ensure the tasks table exists and optionally seed data."""
    for attempt in range(1, INIT_RETRY_ATTEMPTS + 1):
        try:
            with db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(TABLE_DEFINITION)
                    cur.execute("SELECT COUNT(*) FROM tasks")
                    existing_rows = cur.fetchone()[0]

                    if existing_rows == 0 and SEED_TASKS:
                        cur.executemany(
                            "INSERT INTO tasks (title) VALUES (%s)",
                            [(title,) for title in SEED_TASKS],
                        )

                conn.commit()
            app.logger.info("Database initialised (attempt %s)", attempt)
            return
        except psycopg2.OperationalError as exc:
            app.logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                INIT_RETRY_ATTEMPTS,
                exc,
            )
            time.sleep(INIT_RETRY_DELAY)
        except psycopg2.Error as exc:
            app.logger.exception("Unexpected database error during init: %s", exc)
            return

    app.logger.error(
        "Failed to initialise database after %s attempts",
        INIT_RETRY_ATTEMPTS,
    )


def serialise_task(row: psycopg2.extras.RealDictRow) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": row["completed"],
    }


# Run database initialisation at import time so the container is ready for traffic
init_db()


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        with db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify({"status": "ok"}), 200
    except psycopg2.Error as exc:
        return jsonify({"status": "error", "details": str(exc)}), 503


@app.route("/api/tasks", methods=["GET", "POST"])
def tasks_collection():
    if request.method == "GET":
        try:
            with db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(
                        "SELECT id, title, completed FROM tasks ORDER BY id DESC"
                    )
                    rows = cur.fetchall()
            tasks = [serialise_task(row) for row in rows]
            return jsonify(tasks), 200
        except psycopg2.Error as exc:
            app.logger.exception("Failed to fetch tasks")
            return jsonify({"error": "Database error", "details": str(exc)}), 503

    # POST path
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        with db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed",
                    (title,),
                )
                new_task = cur.fetchone()
            conn.commit()
        return jsonify(serialise_task(new_task)), 201
    except psycopg2.Error as exc:
        app.logger.exception("Failed to create task")
        return jsonify({"error": "Database error", "details": str(exc)}), 503


@app.route("/api/tasks/<int:task_id>", methods=["PUT", "DELETE"])
def task_item(task_id: int):
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        updates = []
        values = []

        if "title" in data:
            title = (data.get("title") or "").strip()
            if not title:
                return jsonify({"error": "Title cannot be empty"}), 400
            updates.append("title = %s")
            values.append(title)

        if "completed" in data:
            completed = data.get("completed")
            if isinstance(completed, bool) or completed in (0, 1):
                updates.append("completed = %s")
                values.append(bool(completed))
            else:
                return jsonify({"error": "Completed must be a boolean"}), 400

        if not updates:
            return jsonify({"error": "No fields provided to update"}), 400

        values.append(task_id)
        update_sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s RETURNING id, title, completed"

        try:
            with db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(update_sql, tuple(values))
                    updated_task = cur.fetchone()
                    if not updated_task:
                        conn.rollback()
                        return jsonify({"error": "Task not found"}), 404
                conn.commit()
            return jsonify(serialise_task(updated_task)), 200
        except psycopg2.Error as exc:
            app.logger.exception("Failed to update task")
            return jsonify({"error": "Database error", "details": str(exc)}), 503

    # DELETE path
    try:
        with db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
                deleted = cur.fetchone()
                if not deleted:
                    conn.rollback()
                    return jsonify({"error": "Task not found"}), 404
            conn.commit()
        return "", 204
    except psycopg2.Error as exc:
        app.logger.exception("Failed to delete task")
        return jsonify({"error": "Database error", "details": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
