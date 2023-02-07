from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired
from datetime import datetime, timedelta
from fantasy_chess.models import League

class CreateLeagueForm(FlaskForm):
    league_name = StringField('League Name', validators=[DataRequired('League Name Required')])
    league_start = DateTimeField('League Start', validators=[DataRequired('League Starting date Required')])
    league_end = DateTimeField('League End', validators=[DataRequired('League Ending Date Required')])
    league_type = SelectField('League Type', validators=[DataRequired('League Type Required')])
    submit = SubmitField('Create League')

    def validate_league_name(self, league_name):
        league_title = League.query.filter_by(title=league_name.data).first()
        if league_title:
            raise ValidationError('Choose a different league name, that name is already taken')

    #Validate that the starting date is after today, before the ending date and that the duration is less than 1 year but more than a month.
    def validate_league_start(self, league_start):
        if league_start.data < datetime.utcnow():
            raise ValidationError(f"Please choose a starting date later than the current date")
        elif (self.league_end.data - league_start.data) < timedelta(days=28):
            #This covers the case where league_start > league end
            raise ValidationError(f"Please choose a league duration greater than 28 days")
        elif (league_start.data - self.league_end.data) > timedelta(365):
            raise ValidationError(f"Please choose a league duration shorter than 1 year ")
        






