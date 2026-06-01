from flask import Flask, request, jsonify, render_template
import os
import json
from datetime import datetime

app = Flask(__name__)

def load_tasks():
    data_file = os.getenv("DATA_FILE", "tasks.json")  # ✅ har baar fresh read
    if not os.path.exists(data_file):
        return []
    with open(data_file, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    data_file = os.getenv("DATA_FILE", "tasks.json")  # ✅ har baar fresh read
    with open(data_file, "w") as f:
        json.dump(tasks, f, indent=2)
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html", version=APP_VERSION, environment=ENVIRONMENT)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": APP_VERSION, "environment": ENVIRONMENT})


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "done": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task["done"] = data.get("done", task["done"])
    task["title"] = data.get("title", task["title"])
    save_tasks(tasks)
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return jsonify({"message": "Task deleted"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = ENVIRONMENT == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
