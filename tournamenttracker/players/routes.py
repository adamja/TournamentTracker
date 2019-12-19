from flask import render_template, Blueprint, flash, redirect, url_for, request
from tournamenttracker import db
from tournamenttracker.models import Game, Tournament, Player
from tournamenttracker.players.forms import NewPlayerForm, UpdatePlayerForm
from tournamenttracker.players.utils import save_picture


players_bp = Blueprint('players', __name__)


@players_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/players",
                  methods=['GET', 'POST'])
def players(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    ps = tournament.players
    return render_template('players.html', game=game, tournament=tournament, players=ps)


@players_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/player/<int:player_id>",
                  methods=['GET', 'POST'])
def player(game_id, tournament_id, player_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    p = Player.query.get_or_404(player_id)
    return render_template('player.html', game=game, tournament=tournament, player=p)


@players_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/players/add",
                  methods=['GET', 'POST'])
def new_player(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    form = NewPlayerForm()
    form.tournament_id = tournament_id
    empty_player = Player(name='New Player', game_name='Game Name', image_file='default.jpg')
    if form.validate_on_submit():
        p = Player(name=form.name.data,
                   game_name=form.game_name.data,
                   tournament_id=tournament_id,
                   start_points=form.start_points.data)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            p.image_file = picture_file
        db.session.add(p)
        db.session.commit()
        flash('Your player has been created!', 'success')
        return redirect(url_for('players.players', game_id=game_id, tournament_id=tournament_id))
    return render_template('player_new.html', title='New Player', game=game, tournament=tournament,
                           player=empty_player, form=form)


@players_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/player/<int:player_id>/update",
                  methods=['GET', 'POST'])
def update_player(game_id, tournament_id, player_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    form = UpdatePlayerForm()
    form.tournament_id = tournament_id
    p = Player.query.get_or_404(player_id)
    form.player = p
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            p.image_file = picture_file
            # TODO: could write a function to clean up unused image files when a user successfully changes the image_file
        p.name = form.name.data
        p.game_name = form.game_name.data
        p.start_points = form.start_points.data
        db.session.commit()  # sqlalechmy allows you to update the user by just changing the current user
        flash('Your player has been updated!', 'success')
        return redirect(url_for('players.players', game_id=game_id, tournament_id=tournament_id, player_id=player_id))
    elif request.method == 'GET':
        form.name.data = p.name
        form.game_name.data = p.game_name
        form.start_points.data = p.start_points
    image_file = url_for('static', filename='player_pics/' + p.image_file)
    return render_template('player_update.html', title='Player Info', game=game, tournament=tournament, player=p,
                           image_file=image_file, form=form)


@players_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/player/<int:player_id>/delete", methods=['POST'])
def delete_player(game_id, tournament_id, player_id):
    player = Player.query.get_or_404(player_id)
    # TODO: logged in user is allowed to edit tournament
    db.session.delete(player)
    db.session.commit()
    flash(f'{player.name} has been deleted!', 'success')
    return redirect(url_for('players.players', game_id=game_id, tournament_id=tournament_id))
