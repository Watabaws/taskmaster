from flask import Blueprint, jsonify, request, redirect, url_for
from app.models import db, Task

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # TODO: future pagination query of tasks for homepage
    task = Task.query.get_or_404(task_id)
    return jsonify(task)


@api.route('/api/tasks', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    description = request.form.get('description', '')
    task = Task(name=title, description=description)

    db.session.add(task)
    db.session.commit()

    # TODO: set up a proper API response
    # return {
    #     'id': task.id,
    #     'name': task.name,
    #     'description': task.description,
    #     'created_at': task.created_at,
    #     'is_completed': task.is_completed
    # }

    return redirect(url_for('main.index'))

@api.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('main.index'))
