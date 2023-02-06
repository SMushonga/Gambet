from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

class Tournament_Form(FlaskForm):
    Title = StringField('Title', validators=[DataRequired('Player Name Required'), Length(min=3, message='Player Name must be longer than 3 characters')])
    Start = DateTimeField('Starting Date')
    End = DateTimeField('Ending Date')
    Tournament_Type = SelectField('Tournament Type', choices=[('online', 'otb')], validators=[DataRequired('Choice Required')])

class Player_Form(FlaskForm):
    Name = StringField('Name', validators=[DataRequired('Player Name Required'), Length(min=3, message='Player Name must be longer than 3 characters')])
    Rating = IntegerField('Rating', validators=[DataRequired('Rating Required')])
    Cost = IntegerField('Cost', validators=[DataRequired('Player Cost Required')])
    Birthdate = DateTimeField('Birthdate')

    Lichess_Username = StringField('Lichess Username')
    Chesscom_Username = StringField('Chess.com Username')

class News_Form(FlaskForm):
    Title = StringField(validators=[DataRequired('Title can not be empty')])
    content = TextAreaField(validators=[DataRequired('Please attach content to your article'), Length(min=800, max=10000, message='Content must be more than 800 characters but less than 10000')])