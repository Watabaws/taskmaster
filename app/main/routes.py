from flask import Blueprint, render_template
from app.models import Task

main = Blueprint('main', __name__)

@main.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('main/index.html', tasks=tasks)
