from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from tournamenttracker import db

from tournamenttracker.models import Game
from flask_login import current_user, login_required


games = Blueprint('games', __name__)


@games.route("/game/<int:game_id>", methods=['GET', 'POST'])
def game(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game.html', title=game.name, game=game)
