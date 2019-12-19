from datetime import datetime, timedelta
import math
from flask import current_app, json, jsonify, url_for
from tournamenttracker import db, login_manager
from flask_login import UserMixin


# many to many relationships: https://www.youtube.com/watch?v=OvhoYbjtiKc
# many to many relationships: https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
# many to one relationships: https://www.youtube.com/watch?v=juPQ04_twtA

class BalanceMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    sequence = db.Column(db.String(200))
    description = db.Column(db.String(200), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship('Match', backref='balance_mode', lazy=True)

    def __repr__(self):
        return f"BalanceMode(Name: '{self.name}')"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sequence': self.sequence_list(),
            'description': self.description
        }

    def sequence_list(self):
        """ Convert the string comma separated balance sequence list to an int list """
        if self.sequence:
            sequence_list = self.sequence.split(',')
            for n in range(len(sequence_list)):
                sequence_list[n] = int(sequence_list[n])
            return sequence_list
        return None


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    tournaments = db.relationship('Tournament', backref='game', lazy=True)

    def __repr__(self):
        return f"Game(Name: '{self.name}')"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_file': self.image_file,
            'image_file_url': self.image_file_url()
        }

    def image_file_url(self):
        return url_for('static', filename='game_logos/' + self.image_file)


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    win_points = db.Column(db.Integer, nullable=False, default=2)
    draw_points = db.Column(db.Integer, nullable=False, default=1)
    mvp_points = db.Column(db.Integer, nullable=False, default=1)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    matches = db.relationship('Match', backref='tournament', lazy=True)
    players = db.relationship('Player', backref='tournament', lazy=True)

    def __repr__(self):
        return f"Tournament(Name: '{self.name}', Game: '{self.game}')"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'game': self.game.to_json() if self.game else None
        }

    def rank_players(self):
        player_dict = {}

        for player in self.players:
            player_dict[player.id] = player.calculate_rating()

        ranked = sorted(player_dict, key=player_dict.get, reverse=True)

        updated = False
        rank = 1
        for player_id in ranked:
            player = Player.query.get(player_id)

            if player.tournament_rank != rank:
                player.tournament_rank = rank
                updated = True
                # db.session.commit()

            rank += 1

        if updated:
            db.session.commit()


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    teams_count = db.Column(db.Integer, nullable=False, default=2)
    players_count = db.Column(db.Integer, nullable=False, default=10)
    winning_team = db.Column(db.Integer)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    balance_mode_id = db.Column(db.Integer, db.ForeignKey('balance_mode.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    players = db.relationship('Player', secondary='match_player')

    def __repr__(self):
        return f"Match(Name: '{self.name}', Status: '{self.status()}')"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration(),
            'status': self.status(),
            'teams_count': self.teams_count,
            'players_count': self.players_count,
            'winning_team': self.winning_team,
            'balance_mode_id': self.balance_mode_id,
            'tournament_id': self.tournament_id,
            'ranked_players_list': self.rank_players_list(),
            'balance_mode': self.balance_mode.to_json() if self.balance_mode else None,
            # 'players': [player.to_json() for player in self.players] if self.players else None
            'match_players': [match_player.to_json() for match_player in self.match_players] if self.match_players else None
        }

    def start(self, balance_mode_id):
        """ Function to start a match.
        Returns True on success, and False on failure """
        if self.start_time or self.end_time:
            return False
        self.start_time = datetime.utcnow()
        self.balance_mode_id = balance_mode_id
        return True

    def end(self, winning_team):
        """ Function to end a match.
         Returns True on success, and False on failure """
        if not self.start_time or self.end_time:
            return False
        self.end_time = datetime.utcnow()
        self.winning_team = winning_team
        return True

    def player_in_active_match(self):
        for player in self.players:
            if player.in_live_match():
                return True
        return False

    def duration(self):
        """ Calculate the duration of a match """
        if self.start_time and self.end_time:
            temp = self.end_time - self.start_time
            return self.end_time - self.start_time
        else:
            return None

    def status(self):
        """ Return the current state of the match.
        Options: Not started, In progress or Complete """
        if self.start_time and self.end_time:
            return 'Complete'
        elif self.start_time:
            return 'In progress'
        else:
            return 'Not started'

    def rank_players_list(self):
        """ Rank match players in order of highest rating to lowest.
        Return ranked array of match players_id's """
        player_dict = {}

        for player in self.players:
            player_dict[player.id] = player.calculate_rating()

        ranked = sorted(player_dict, key=player_dict.get, reverse=True)
        return ranked

    def player_positions(self):
        """ Returns a dictionary containing the teams, positions and player_id in each position """
        positions = {}  # positions dictionary to be returned by function
        teams = self.teams_count
        players = self.players_count
        players_per_team = int(players / teams)
        player_balance_list = []

        if self.status() != 'Not started':  # if the game has already started, get the player current positions
            return self.player_current_positions()
        elif self.balance_mode.name == 'Auto':
            player_balance_list = self.auto_balance()
            positions['balanced'] = True
        elif self.balance_mode.name == 'Manual':
            player_balance_list = self.rank_players_list()
            positions['balanced'] = False
        else:
            player_balance_list = self.player_balance_positions_list(self.balance_mode)
            positions['balanced'] = True

        positions['players'] = {}

        pos = 1
        for t in range(teams):
            for p in range(players_per_team):
                if len(player_balance_list) >= pos:
                    player_id = player_balance_list[pos-1]  # get player_id from the balance list
                    if player_id:
                        positions['players'][player_id] = {}
                        positions['players'][player_id]['team'] = t + 1  # add team to player_id
                        positions['players'][player_id]['position'] = pos  # add position to player_id
                pos += 1

        return positions

    def player_current_positions(self):
        """ Returns a dictionary containing the current match player positions """
        positions = {}  # positions dictionary to be returned by function
        player_balance_list = self.player_balance_positions_list(self.balance_mode)

        positions['balanced'] = True
        positions['players'] = {}

        for mp in self.match_players:
            positions['players'][mp.player_id] = {}
            positions['players'][mp.player_id]['team'] = mp.team  # add team to player_id
            positions['players'][mp.player_id]['position'] = mp.position  # add position to player_id
            positions['players'][mp.player_id]['won'] = mp.won
            positions['players'][mp.player_id]['mvp'] = mp.mvp

        return positions

    def all_balance_mode_positions_dict(self):
        balance_modes = BalanceMode.query.all()
        balance_mode_pos_dict = {}

        for balance_mode in balance_modes:
            balance_mode_pos_dict[balance_mode.id] = self.player_balance_positions_list(balance_mode)

        return balance_mode_pos_dict

    def player_balance_positions_list(self, balance_mode):
        """ Returns a list that contains the in order positions of player_id's based on the players current ranking and
            the balance_mode selected """
        if balance_mode.name == 'Manual':
            return None
        elif balance_mode.name == 'Auto':
            return self.auto_balance()

        players_ranked = self.rank_players_list()
        balance_sequence = balance_mode.sequence_list()
        player_position_list = []

        for n in balance_sequence:
            if n <= len(players_ranked):
                player_position_list.append(players_ranked[n-1])
            else:
                player_position_list.append(None)

        return player_position_list

    def auto_balance(self):
        """ Auto balance a game if it has 2 teams and 10 players """
        if not (self.teams_count == 2 and len(self.players) == 10):  # TODO: remove this
            return self.rank_players_list()
        players_list = self.rank_players_list()
        teams = self.teams_count
        players = self.players_count
        p1, p2, p3, p4, p5 = 1, 2, 3, 4, 5

        total_player_points = 0
        for p in self.players:
            total_player_points += p.calculate_rating()

        best_difference = total_player_points  # set the best difference to the total player points as this is the worst balance condition
        best_team = []

        # find the team combination with the closest 50/50 balance
        while p2 <= players - 3:
            while p3 <= players - 2:
                while p4 <= players - 1:
                    while p5 <= players:
                        team_rating = 0
                        team_rating += Player.query.get(players_list[p1 - 1]).calculate_rating()
                        team_rating += Player.query.get(players_list[p2 - 1]).calculate_rating()
                        team_rating += Player.query.get(players_list[p3 - 1]).calculate_rating()
                        team_rating += Player.query.get(players_list[p4 - 1]).calculate_rating()
                        team_rating += Player.query.get(players_list[p5 - 1]).calculate_rating()
                        difference = abs((total_player_points / 2) - team_rating)

                        if difference < best_difference:
                            best_difference = difference

                            best_team = [p1, p2, p3, p4, p5]

                        p5 += 1

                    p4 += 1
                    p5 = p4 + 1

                p3 += 1
                p4 = p3 + 1

            p2 += 1
            p3 = p2 + 1

        # create team list
        cursor_team1 = 0  # position cursor for team 1
        cursor_team2 = 5  # position cursor for team 2
        auto_balanced_team = [None] * players  # create an empty list of size players to put players positions into
        for n in range(len(players_list)):
            if n + 1 in best_team:
                auto_balanced_team[cursor_team1] = players_list[n]
                cursor_team1 += 1
            else:
                auto_balanced_team[cursor_team2] = players_list[n]
                cursor_team2 += 1

        return auto_balanced_team

    def balance_mode_name(self):
        if self.balance_mode:
            return self.balance_mode.name
        else:
            return None

    @staticmethod
    def format_datetime(t):
        """ Format a passed datetime to a datetime string in the format YYYY:MM:DD H:MM:SS """
        if isinstance(t, datetime):
            return t.strftime('%Y-%m-%d %H:%M:%S')
        return None

    @staticmethod
    def format_time(t):
        """ Format a passed datetime to a time string in the format H:MM:SS """
        if isinstance(t, datetime):
            if t.hour > 0:
                return t.strftime('%H:%M:%S')
            else:
                return t.strftime('%M:%S')
        return None

    @staticmethod
    def format_timedelta(t):
        """ Format a passed timedelta to a time string in the format H:MM:SS """
        if isinstance(t, timedelta):
            t = t.total_seconds()
            hours = t // 3600
            s = t - (hours * 3600)  # remaining seconds
            minutes = s // 60  # minutes
            seconds = s - (minutes * 60)  # remaining seconds
            if hours > 0:
                return '{:02}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))   # total time
            else:
                return '{:02}:{:02d}'.format(int(minutes), int(seconds))  # total time
        return None


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    game_name = db.Column(db.String(20))
    tournament_rank = db.Column(db.Integer, nullable=False, default=0)
    win_score = db.Column(db.Integer, nullable=False, default=0)
    draw_score = db.Column(db.Integer, nullable=False, default=0)
    lose_score = db.Column(db.Integer, nullable=False, default=0)
    mvp_score = db.Column(db.Integer, nullable=False, default=0)
    start_points = db.Column(db.Integer, nullable=False, default=0)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    matches = db.relationship('Match', secondary='match_player')

    def __repr__(self):
        return f"Player(Name: '{self.name}', Game_name: '{self.game_name}', Rank: {self.rank})"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'game_name': self.game_name,
            'tournament_rank': self.tournament_rank,
            'win_score': self.win_score,
            'draw_score': self.draw_score,
            'lost_score': self.lose_score,
            'mvp_score': self.mvp_score,
            'image_file': self.image_file,
            'image_file_url': self.image_file_url(),
            'tournament_id': self.tournament_id,
            'win_rate_percentage': self.win_rate_percentage(),
            'rating': self.calculate_rating(),
            'in_live_match': self.in_live_match(),
            'tournament': self.tournament.to_json() if self.tournament else None
            # 'matches': [match.to_json() for match in self.matches] if self.matches else None
        }

    def update_stats(self):
        """ Update the player stats based on previous completed matches """
        wins, draws, loses, mvps = 0, 0, 0, 0

        for mp in self.match_players:
            if mp.won:
                wins += 1
            if mp.draw:
                draws += 1
            if mp.lost:
                loses += 1
            if mp.mvp:
                mvps += 1

        # update the database only if the stats have changed
        updated = False
        if self.win_score != wins:
            self.win_score = wins
            updated = True
        if self.draw_score != draws:
            self.draw_score = draws
            updated = True
        if self.lose_score != loses:
            self.lose_score = loses
            updated = True
        if self.mvp_score != mvps:
            self.mvp_score = mvps
            updated = True

        if updated:
            db.session.commit()

    def win_rate_percentage(self):
        """ Calculate the player win to loss rate percentage """
        self.update_stats()  # update the stats before calculating the player win percentage
        if self.win_score == 0 and self.lose_score == 0:
            return '-'
        # elif self.lose_score == 0:
        #     return 'inf'
        else:
            matches_played = self.win_score + self.lose_score
            return round((self.win_score/matches_played)*100)

    def calculate_rating(self):
        """ Calculate the player rating based on previous game statistics
            Win = 2 point, Draw = 1 points, MVP = 1 points """
        self.update_stats()  # update stats before calculating the player rating
        win_points = self.tournament.win_points

        return round((self.tournament.win_points * self.win_score) +
                     (self.tournament.draw_points * self.draw_score) +
                     (self.tournament.mvp_points * self.mvp_score) +
                     self.start_points, 1)

    def in_live_match(self):
        """ Check to see if the player is in any running matches.
            Returns: True if they are or False if they are not """
        for mp in self.match_players:
            if mp.match.status() == 'In progress':
                return True
        return False

    def image_file_url(self):
        return url_for('static', filename='player_pics/' + self.image_file)


class MatchPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    won = db.Column(db.Boolean, default=False)
    draw = db.Column(db.Boolean, default=False)
    lost = db.Column(db.Boolean, default=False)
    mvp = db.Column(db.Boolean, default=False)
    start_rating = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    match = db.relationship(Match, backref=db.backref('match_players', cascade='all, delete-orphan'))
    player = db.relationship(Player, backref=db.backref('match_players', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"MatchPlayer(Player: '{self.player.name}', Match: '{self.match.name}', Status: '{self.match.status}')"

    def to_json(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'player_id': self.player_id,
            'team': self.team,
            'position': self.position,
            'won': self.won,
            'draw': self.draw,
            'mvp': self.mvp,
            'start_rating': self.start_rating,
            # 'match': self.match.to_json() if self.match else None,
            'player': self.player.to_json() if self.player else None
        }

    def match_start(self, team, position, rating):
        self.team = int(team)
        self.position = int(position)
        self.start_rating = int(rating)

    def match_end(self, winning_team, mvp):
        if self.team == int(winning_team):
            self.won = True
        elif 0 == int(winning_team):  # not used at the moment, figure out how to choose draws later
            self.draw = True
        else:
            self.lost = True

        if self.player_id == int(mvp):
            self.mvp = True
        return True

    def match_status(self):
        """ Return a string stating if the player won, drew or lost a match. None if match not played """
        if self.won:
            return 'Won'
        elif self.draw:
            return 'Drew'
        elif self.lost:
            return 'Lost'
        else:
            return None

# a function needed to reload the user from the user_id stored in the session
# taken from the login_manager website
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # will add a default.jpg later
    password = db.Column(db.String(60), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    tournaments = db.relationship('Tournament', backref='creator', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
