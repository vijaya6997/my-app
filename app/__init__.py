import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Database connectivity check with automatic fallback
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'mysql' in db_uri:
        try:
            from sqlalchemy import create_engine
            # Quick check to see if the database server is reachable
            engine = create_engine(db_uri)
            engine.connect().close()
            print("Successfully connected to MySQL database!")
        except Exception as e:
            print(f"Warning: Could not connect to MySQL ({e}).")
            print("Falling back to local SQLite database for this session...")
            # Fallback to SQLite
            db_path = os.path.join(app.instance_path, 'freelance.db')
            if not os.path.exists(app.instance_path):
                os.makedirs(app.instance_path)
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    db.init_app(app)
    login_manager.init_app(app)

    from . import models
    from .routes.main import main
    from .routes.auth import auth
    from .routes.jobs import jobs
    from .routes.messages import messages

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(jobs)
    app.register_blueprint(messages)

    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app
