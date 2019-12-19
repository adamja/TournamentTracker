from flask import render_template, Blueprint, flash, redirect, url_for, request
from tournamenttracker import db
from tournamenttracker.models import Game, Tournament, Player, Match, BalanceMode
from tournamenttracker.tournaments.forms import NewTournamentForm, UpdateTournamentForm


tournaments = Blueprint('tournaments', __name__)


@tournaments.route("/game/<int:game_id>/tournament/<int:tournament_id>")
def tournament(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.rank_players()  # rank players based on current rating
    players = tournament.players
    return render_template('tournament.html', game=game, tournament=tournament, players=players)


@tournaments.route("/tournament/add", methods=['GET', 'POST'])
def new_tournament():
    form = NewTournamentForm()
    form.game.choices = get_game_choices()
    if form.validate_on_submit():
        t = Tournament(name=form.name.data, game_id=form.game.data, user_id=1)
        db.session.add(t)
        db.session.commit()
        flash('Your tournament has been created!', 'success')
        return redirect(url_for('tournaments.tournament', game_id=t.game_id, tournament_id=t.id))
    return render_template('tournament_new.html', title='New Tournament', form=form)


@tournaments.route("/game/<int:game_id>/tournament/<int:tournament_id>/settings", methods=['GET', 'POST'])
def update_tournament(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    form = UpdateTournamentForm()
    form.game.choices = get_game_choices()
    form.tournament = tournament

    if form.validate_on_submit():
        tournament.name = form.name.data
        tournament.game_id = form.game.data
        tournament.win_points = form.win_points.data
        tournament.draw_points = form.draw_points.data
        tournament.mvp_points = form.mvp_points.data
        db.session.commit()
        flash('Your tournament has been updated!', 'success')
        return redirect(url_for('tournaments.tournament', game_id=game_id, tournament_id=tournament_id))
    elif request.method == 'GET':
        form.name.data = tournament.name
        form.game.data = tournament.game_id
        form.win_points.data = tournament.win_points
        form.draw_points.data = tournament.draw_points
        form.mvp_points.data = tournament.mvp_points
    return render_template('tournament_update.html', title='Tournament Settings',
                           game=game, tournament=tournament, form=form)


@tournaments.route("/tournament/<int:tournament_id>/delete", methods=['POST'])
def delete_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    # TODO: logged in user is allowed to edit tournament
    db.session.delete(tournament)
    db.session.commit()
    flash(f'{tournament.name} has been deleted!', 'success')
    return redirect(url_for('main.home'))


def get_game_choices():
    return [(game.id, game.name) for game in Game.query.order_by('name')]
