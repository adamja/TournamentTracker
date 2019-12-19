from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, IntegerField, SelectField, widgets, SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from tournamenttracker.models import Match


class NewMatchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    teams = IntegerField('Teams', validators=[DataRequired()])
    players = IntegerField('Players', validators=[DataRequired()])
    balance_mode = SelectField('Balance mode', choices=[], coerce=int)
    submit = SubmitField('Create')

    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        match = Match.query.filter_by(tournament_id=self.tournament_id, name=name.data).first()
        if match:
            raise ValidationError('That name is taken. Please choose a different one.')

    def validate_teams(self, teams):
        """ Validate that the teams count is equal to 2 """
        if teams.data != 2:
            raise ValidationError('You can only choose a team size of 2.')

    def validate_players(self, players):
        """ Validate that the players count is even and above 1 """
        if players.data < self.teams.data:
            raise ValidationError('You cannot have more teams than players.')
        if players.data % 2 > 0:
            raise ValidationError('You must have an even amount of players.')


class UpdateMatchForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    teams = IntegerField('Teams', validators=[DataRequired()])
    players = IntegerField('Players', validators=[DataRequired()])
    balance_mode = SelectField('Balance mode', choices=[], coerce=int)
    submit = SubmitField('Update')

    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        if self.match.name != name.data:
            match = Match.query.filter_by(tournament_id=self.tournament_id, name=name.data).first()
            if match:
                raise ValidationError('That name is taken. Please choose a different one.')

    def validate_teams(self, teams):
        """ Validate that the teams count is equal to 2 """
        if teams.data != 2:
            raise ValidationError('You can only choose a team size of 2.')

    def validate_players(self, players):
        """ Validate that the players count is even and above 1 """
        if players.data < self.teams.data:
            raise ValidationError('You cannot have more teams than players.')
        if players.data % 2 > 0:
            raise ValidationError('You must have an even amount of players.')


class PlayMatchForm(FlaskForm):
    balance_mode = SelectField('Balance mode', choices=[], coerce=int)
    winning_team = SelectField('Winning team', choices=[], coerce=int)
    mvp = SelectField('MVP', choices=[], coerce=int)
    submit = SubmitField('End')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddPlayersMatchForm(FlaskForm):
    players = MultiCheckboxField('Select players for the match', choices=[], coerce=int)
    submit = SubmitField('Update')

    def validate_players(self, players):
        """ Validate that the players selected is not more than the players for the match """
        if self.match.status() != 'Not started':
            raise ValidationError(f'You cannot add or remove players in a match that has already started.')
        if len(players.raw_data) > self.match.players_count:
            raise ValidationError(f'You have selected {len(players.raw_data)} players, but the maximum is {self.match.players_count} for the match.')
