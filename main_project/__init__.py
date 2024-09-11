from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from main_project.config import Config  # Absolute import

bcrypt = Bcrypt()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db=SQLAlchemy(app)
    bcrypt.init_app(app)
    
    
    # Register blueprints
    with app.app_context():
        from .blueprints.student import student_bp
        from .blueprints.professor import professor_bp
        from .blueprints.other import others_bp
        from .blueprints.auth import auth_bp

        app.register_blueprint(student_bp, url_prefix='/student')
        app.register_blueprint(professor_bp, url_prefix='/professor')
        app.register_blueprint(others_bp, url_prefix='/other')
        app.register_blueprint(auth_bp)

    return app
