from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Redirect to login page if not authenticated
login_manager.login_message_category = 'info' #flash message catagory

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    password = os.getenv('MYSQL_PASSWORD')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://yanick2:{password}@yanick2.mysql.pythonanywhere-services.com/yanick2$inventar_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence a warning

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import bp  # Import here to avoid circular imports
    app.register_blueprint(bp)

    # with app.app_context():
        # db.create_all() #Move to the models.py file

    return app
