from flask import Blueprint, render_template
from app.models import Task

main = Blueprint('main', __name__)

@main.route('/')
def index():
    completed_tasks = Task.query.filter_by(is_completed=False).all()
    return render_template('main/index.html', tasks=completed_tasks)
