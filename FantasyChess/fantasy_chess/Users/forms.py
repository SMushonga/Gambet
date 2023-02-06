from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from fantasy_chess.models import User

class ContactUsForm(FlaskForm):
    #Consider adding a selectfield to easily categorise the type of query
    category = SelectField(f'Query Category', choices=[('Query', 'Query'), ('Ticket','Ticket')])
    content = TextAreaField('Query', validators=[DataRequired(), Length(min=10)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=100)])
    submit = SubmitField('Send')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    teamname = StringField('Teamname', validators=[DataRequired(), Length(min=4, max=50)])
    submit = SubmitField('Sign Up')

    def validate_teamname(self, teamname):
        user = User.query.filter_by(teamname=teamname.data).first()
        if user:
            raise ValidationError(f'{teamname.data} is taken. Please choose a different teamname.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address already has an associated account. Try loginning in, or use a different email address.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('We cannot reset your password as there is no account with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
