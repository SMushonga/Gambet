from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from fantasy_chess.config import Config


#Initialising an instance of the database, login/user management, mail and password cryptology
bcrypt = Bcrypt()
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
mail = Mail()  

def create_app(config_class=Config):
    #Passing our app variable into the instance.
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    #Importing blueprints
    from fantasy_chess.Errors.handlers import errors
    from fantasy_chess.Fantasy.routes import fantasy
    from fantasy_chess.League.routes import league
    from fantasy_chess.Payments.routes import payments
    from fantasy_chess.Teams.routes import teams
    from fantasy_chess.Users.routes import users
    from fantasy_chess.Insert.routes import insert

    #Registering different parts of our app as blueprints for compartmentalisation.
    app.register_blueprint(errors)
    app.register_blueprint(fantasy)
    app.register_blueprint(league)
    app.register_blueprint(payments)
    app.register_blueprint(teams)
    app.register_blueprint(users)
    app.register_blueprint(insert)

    from fantasy_chess.Payments.functions import insert_products
    insert_products()

    return app