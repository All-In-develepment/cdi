from flask import Flask
from .models import db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/cdi_db?client_encoding=utf8'
    db.init_app(app)
    app.config['SECRET_KEY'] = 'minhachavekey'
    # Registrar as rotas
    with app.app_context():
        register_routes()

    return app
