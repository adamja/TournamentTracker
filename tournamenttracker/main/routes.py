import os
from flask import render_template, request, Blueprint, send_from_directory, current_app
from tournamenttracker.models import Game, Tournament


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    games = Game.query.order_by(Game.name.asc()).all()
    tournaments = Tournament.query.order_by(Tournament.name.asc()).all()
    return render_template('home.html', games=games, tournaments=tournaments)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
