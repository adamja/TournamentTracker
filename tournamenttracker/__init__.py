# __init__.py tells python that this file is a package and also initialises and ties together
# everything that we need for the app

from flask import Flask
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from tournamenttracker.config import Config

# we leave the extensions outside of the create_app function. The reasoning is:
# this is so that the ext object does not initially get bound to any one application, using this design pattern
# no application specific state is stored on the ext object, so one ext object can be used for multiple apps

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # pass in the function name of the route
login_manager.login_message_category = 'info'  # change the bootstrap message appearance
mail = Mail()
# flask-assets: https://www.youtube.com/watch?v=HYO6GNOJMmQ
js = Bundle('js-file1.js', 'js-file2.js', output='gen/main.js')

# How to use flask-assets within the html layout:
    # {% assets "main_js" %}
    # <script type="text/javascript" src="{{ ASSETS_URL }}"></script>
    # {% endassets %}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    assets = Environment(app)
    assets.register('main.js', js)

    from tournamenttracker.main.routes import main
    from tournamenttracker.games.routes import games
    from tournamenttracker.tournaments.routes import tournaments
    from tournamenttracker.players.routes import players_bp
    from tournamenttracker.matches.routes import matches_bp
    from tournamenttracker.users.routes import users
    app.register_blueprint(main)
    app.register_blueprint(games)
    app.register_blueprint(tournaments)
    app.register_blueprint(players_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(users)

    return app
