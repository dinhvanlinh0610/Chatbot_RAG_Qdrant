from flask import Flask, request, jsonify
from celery_config import celery
from test import add
app = Flask("myapp")
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"

celery.conf.update(app.config)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/process')
def process():
    task = add.apply_async((2, 3))
    return jsonify(
        {
            "task_id": task.id
        }
    ), 200
@app.route('/result/<task_id>')
def result(task_id):
    task = add.AsyncResult(task_id)
    return jsonify(
        {
            "task_status": task.status,
            "task_result": task.result
        }
    ), 200
if __name__ == '__main__':
    app.run(debug=True)
