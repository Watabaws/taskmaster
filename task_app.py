from pathlib import Path

from flask import Flask, render_template, request

from app.models import db
from app.api.routes import api
from app.main.routes import main



def create_app():
    app = Flask(__name__, template_folder='app/templates')

    db_path = Path(app.root_path) / "tasks.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(api)
    app.register_blueprint(main)

    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


