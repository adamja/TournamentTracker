from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from tournamenttracker.models import Player


class NewPlayerForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    game_name = StringField('Game name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    start_points = IntegerField('Starting points (handicap)')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Create')

    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        player = Player.query.filter_by(tournament_id=self.tournament_id, name=name.data).first()
        if player:
            raise ValidationError('That name is taken. Please choose a different one.')

    def validate_game_name(self, game_name):
        """ Validate that the game_name is unique within the tournament """
        player = Player.query.filter_by(tournament_id=self.tournament_id, game_name=game_name.data).first()
        if player:
            raise ValidationError('That game name is taken. Please choose a different one.')


class UpdatePlayerForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    game_name = StringField('Game name',
                        validators=[DataRequired(), Length(min=2, max=20)])
    start_points = IntegerField('Starting points (handicap)')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # the validate function are built into the wtforms module, pretty cool
    def validate_name(self, name):
        """ Validate that the name is unique within the tournament """
        if self.player.name != name.data:
            player = Player.query.filter_by(tournament_id=self.tournament_id, name=name.data).first()
            if player:
                raise ValidationError('That name is taken. Please choose a different one.')

    def validate_game_name(self, game_name):
        """ Validate that the game_name is unique within the tournament """
        if self.player.game_name != game_name.data:
            player = Player.query.filter_by(tournament_id=self.tournament_id, game_name=game_name.data).first()
            if player:
                raise ValidationError('That game name is taken. Please choose a different one.')
