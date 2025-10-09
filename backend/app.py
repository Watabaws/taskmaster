from flask import Flask, jsonify

app = Flask(__name__)

TASKS = [
    {'id': 1, 'title': 'Containerize backend', 'done': False},
    {'id': 2, 'title': 'Deploy to Minikube', 'done': False}
]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    # CORS header required for the frontend to access this API
    response = jsonify(TASKS)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

