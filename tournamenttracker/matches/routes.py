from flask import render_template, Blueprint, flash, redirect, url_for, request, jsonify, get_flashed_messages
from tournamenttracker import db
from tournamenttracker.models import Game, Tournament, Player, Match, MatchPlayer, BalanceMode
from tournamenttracker.matches.forms import NewMatchForm, UpdateMatchForm, PlayMatchForm, AddPlayersMatchForm


matches_bp = Blueprint('matches', __name__)


def get_balance_mode_choices():
    return [(balance_mode.id, balance_mode.name) for balance_mode in BalanceMode.query.order_by('name')]


def get_winning_team_choices(teams_count):
    return [(t+1, f'Team {t+1}') for t in range(teams_count)]


def get_mvp_choices(players):
    choices = [(player.id, player.name) for player in players]
    choices.append((0, 'None'))  # add a none option to the list
    return choices


def get_match_player_choices(tournament):
    choices = [(player.id, player.name) for player in tournament.players]
    choices.sort(key=lambda tup: tup[1])
    return choices


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/matches",
                  methods=['GET', 'POST'])
def matches(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    ms = tournament.matches
    return render_template('matches.html', game=game, tournament=tournament, matches=ms)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>",
                  methods=['GET', 'POST'])
def detail_match(game_id, tournament_id, match_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    m = Match.query.get_or_404(match_id)
    match_players = m.match_players
    return render_template('match.html', game=game, tournament=tournament, match=m, match_players=match_players)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/matches/add",
                  methods=['GET', 'POST'])
def new_match(game_id, tournament_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    form = NewMatchForm()
    form.tournament_id = tournament_id
    form.balance_mode.choices = get_balance_mode_choices()

    if form.validate_on_submit():
        m = Match(name=form.name.data, teams_count=form.teams.data,
                  players_count=form.players.data, balance_mode_id=form.balance_mode.data, tournament_id=tournament_id)
        db.session.add(m)
        db.session.commit()
        flash('Your match has been created!', 'success')
        return redirect(url_for('matches.matches', game_id=game_id, tournament_id=tournament_id))
    elif request.method == 'GET':
        form.name.data = 'Match #'
        form.teams.data = 2
        form.players.data = 10
        form.balance_mode.data = 1  # auto
    return render_template('match_new.html', title='New Match', game=game, tournament=tournament, form=form)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/_balance_mode/<int:balance_mode>")
def balance_mode_match(game_id, tournament_id, match_id, balance_mode_id):
    pass


@matches_bp.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/update",
                  methods=['GET', 'POST'])
def update_match(game_id, tournament_id, match_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    form = UpdateMatchForm()
    form.tournament_id = tournament_id
    form.balance_mode.choices = get_balance_mode_choices()
    m = Match.query.get_or_404(match_id)
    form.match = m

    if form.validate_on_submit():
        m.name = form.name.data
        m.teams_count = form.teams.data
        m.players_count = form.players.data
        m.balance_mode_id = form.balance_mode.data
        db.session.commit()
        flash('Your match has been updated!', 'success')
        return redirect(url_for('matches.matches', game_id=game_id, tournament_id=tournament_id, match_id=match_id))
    elif request.method == 'GET':
        form.name.data = m.name
        form.players.data = m.players_count
        form.teams.data = m.teams_count
        form.balance_mode.data = m.balance_mode_id
    return render_template('match_update.html', title='Match Info',
                           game=game, tournament=tournament, match=m, form=form)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/delete", methods=['POST'])
def delete_match(game_id, tournament_id, match_id):
    match = Match.query.get_or_404(match_id)
    # TODO: logged in user is allowed to edit tournament
    db.session.delete(match)
    db.session.commit()
    flash(f'{match.name} has been deleted!', 'success')
    return redirect(url_for('matches.matches', game_id=game_id, tournament_id=tournament_id))


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/add_players", methods=['GET', 'POST'])
def add_players_match(game_id, tournament_id, match_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    match = Match.query.get_or_404(match_id)
    form = AddPlayersMatchForm()
    form.match = match
    form.players.choices = get_match_player_choices(tournament)
    form.players.data = [player.id for player in match.players]

    if form.validate_on_submit():
        checked = [int(p) for p in form.players.raw_data]
        for player in tournament.players:
            mp = MatchPlayer.query.filter_by(match_id=match.id).filter_by(player_id=player.id).first()
            if player.id in checked:  # player is checked in the form
                if not mp:
                    mp = MatchPlayer(match_id=match.id, player_id=player.id)
                    db.session.add(mp)
            else:
                if mp:
                    db.session.delete(mp)
        db.session.commit()
        flash(f'Match players have been updated!', 'success')
        return redirect(url_for('matches.matches', game_id=game_id, tournament_id=tournament_id, match_id=match_id))

    return render_template('match_add_players.html', title='Add Players to Match',
                           game=game, tournament=tournament, match=match, form=form)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/play",
                  methods=['GET', 'POST'])
def play_match(game_id, tournament_id, match_id):
    game = Game.query.get_or_404(game_id)
    tournament = Tournament.query.get_or_404(tournament_id)
    match = Match.query.get_or_404(match_id)
    form = PlayMatchForm()
    form.balance_mode.choices = get_balance_mode_choices()
    form.winning_team.choices = get_winning_team_choices(match.teams_count)
    form.mvp.choices = get_mvp_choices(match.players)

    if request.method == 'GET':
        form.balance_mode.data = match.balance_mode_id

    return render_template('match_play.html', title=match.name, game=game, tournament=tournament, match=match,
                           form=form)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/start", methods=['POST'])
def start_match(game_id, tournament_id, match_id):
    match = Match.query.get_or_404(match_id)

    if match.status() == 'Not started':
        data = request.get_json()
        success = True
        mp_count = len(match.players)
        if mp_count != match.players_count:  # players count = players length
            success = False
            flash(f'Cannot start match with {mp_count} players when the match is configured for {match.players_count} players.', 'danger')
        if match.player_in_active_match():  # player not in active match
            success = False
            flash('Cannot start a match while a player is in another running match', 'danger')

        if success:
            match.start(data['balance_mode_id'])  # set match: balance_mode, start_time
            for mp in match.match_players:
                pid = str(mp.player_id)
                team = int(data['players'][pid]['team'])
                position = int(data['players'][pid]['position'])
                rating = int(data['players'][pid]['rating'])
                mp.match_start(team, position, rating)  # set match_player: team, position, start_rating
                db.session.add(mp)
            db.session.commit()
            flash(f'The match has started!', 'success')
    else:
        flash(f'You cannot start a match that has finished or already started!', 'danger')
    return url_for('matches.play_match', game_id=game_id, tournament_id=tournament_id, match_id=match.id)


@matches_bp.route("/game/<int:game_id>/tournament/<int:tournament_id>/match/<int:match_id>/end", methods=['POST'])
def end_match(game_id, tournament_id, match_id):
    match = Match.query.get_or_404(match_id)

    if match.status() == 'In progress':
        data = request.get_json()
        winning_team = int(data['winning_team'])
        match.end(winning_team)  # set match: end_time, winning_team
        for mp in match.match_players:
            mvp = int(data['mvp'])
            mp.match_end(winning_team, mvp)  # set match_player: won, draw, lost, mvp
            db.session.add(mp)
        db.session.commit()
        flash(f'The match has ended!', 'success')
    else:
        flash(f'You cannot end a match that has not started or already finished!', 'danger')

    return url_for('matches.play_match', game_id=game_id, tournament_id=tournament_id, match_id=match.id)
