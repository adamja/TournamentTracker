from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from tournamenttracker import db
from tournamenttracker.models import Tournament


class NewTournamentForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    game = SelectField('Game', choices=[], coerce=int)
    win_points = IntegerField('Points for winning', validators=[DataRequired()])
    draw_points = IntegerField('Points for drawing', validators=[DataRequired()])
    mvp_points = IntegerField('Points for MVP', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        tournament = Tournament.query.filter_by(name=name.data).first()
        if tournament:
            raise ValidationError('That name is taken. Please choose a different one.')


class UpdateTournamentForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    game = SelectField('Game', choices=[], coerce=int)
    win_points = IntegerField('Points for winning', validators=[DataRequired()])
    draw_points = IntegerField('Points for drawing', validators=[DataRequired()])
    mvp_points = IntegerField('Points for MVP', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        if self.tournament.name != name.data:
            tournament = Tournament.query.filter_by(name=name.data).first()
            if tournament:
                raise ValidationError('That name is taken. Please choose a different one.')

    def validate_game(self, game):
        """ Validate that the tournament does not have already created matches """
        if self.tournament.game.id != game.data:
            if self.tournament.matches is not None:
                raise ValidationError('You cannot change the game type when the tournament already contains matches.')
