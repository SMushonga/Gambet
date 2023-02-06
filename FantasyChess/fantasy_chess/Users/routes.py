from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db, bcrypt
from fantasy_chess.models import User
from fantasy_chess.Users.forms import ContactUsForm, LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from fantasy_chess.Users.functions import send_reset_email, send_query_email
from werkzeug.urls import url_parse
users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #Immediately hashing the passsword so we never store the users password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(teamname=form.teamname.data, email=form.email.data, full_name=form.fullname.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        #Immediately login log the user into their account after registering
        login_user(user, remember=True)

        flash('Your account has been created, Create your first team!', 'success')
        #We send an email for the user to confirm their account, access to certain features is restricted until then
        return redirect(url_for('teams.transfers'))

    return render_template('register.html', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()
        flash('Current user logged out to allow for new login.', 'failure')
        return redirect(url_for('users.login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            #Check if there is a next page, and that it is a relative address
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('teams.my_team')
            return redirect(next_page) if next_page else redirect(url_for('teams.my_team'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('fantasy.home'))


@users.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profie.html')



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        #We do not need to check if this user exists as the form validator performs this task
        user = User.query.filter_by(email=form.email.data).first()

        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        #user == None indicates the token has raised an error as it is expired or invalid
        flash('That is an invalid or expired token, request another', 'failure')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password

        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)

@users.route("/contact_us", methods=['GET', 'POST'])
def contact():
    form = ContactUsForm()
    if form.validate_on_submit():
        #Mail the form to me
        send_query_email(form.email.data, form.content.data, form.category.date)
        flash('Query Successfuly Sent', 'success')
        return redirect(url_for('fantasy.home'))
    return render_template('contact.html')

@users.route("/register", methods=['GET', 'POST'])
def register():
