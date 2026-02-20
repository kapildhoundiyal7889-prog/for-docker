from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = "database.db"


# -------------------------
# Database Helper Functions
# -------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Initialize DB on start
init_db()


# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return jsonify({"message": "Task Manager API Running"})


# Create Task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (title, description, created_at) VALUES (?, ?, ?)",
        (data["title"], data.get("description", ""), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Task created successfully"}), 201


# Get All Tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    return jsonify([dict(task) for task in tasks])


# Update Task Status
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    if "status" not in data:
        return jsonify({"error": "Status is required"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (data["status"], task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated successfully"})


# Delete Task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
