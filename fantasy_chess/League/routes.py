from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db, bcrypt
from fantasy_chess.models import User, League, User_League
from fantasy_chess.League.forms import CreateLeagueForm
from fantasy_chess.League.functions import create_league_function, join_league_function

league = Blueprint('league', __name__)

@league.route("/create_league", methods=['GET', 'POST'])
@login_required
def create_league():
    form = CreateLeagueForm()
    if form.validate_on_submit():
        if create_league_function(form.league_name.data, form.league_start.data, form.league_end.data, current_user):
            flash('Successfully created a league', 'success')
            return redirect(url_for('league.leagues'))
        else:
            flash('You have already created 3 leagues - the maximum for non-premium members')
            return redirect(url_for('league.leagues'))
    return render_template('create_league.html', form=form)


@league.route("/league/<int:league_id>", methods=['GET', 'POST'])
@login_required()
def league_page(league_id):
    league_object = League.query.get_or_404(league_id)
    user_leagues = User_League.query.filter_by(league_id=league_id).order_by(User_League.position.asc()).all()
    render_template('league.html', league_object=league_object, user_leagues=user_leagues)

@league.route("/leagues", methods=['GET', 'POST'])
@login_required
def leagues():
    if request.method == 'POST' and request.form.get('league_code'):
        if join_league_function(request.form.get('league_code'), current_user):
            flash('Successfully joined league', 'success')
            return redirect(url_for('league.leagues'))
        else:
            flash('There is no league with that joining code')
            return redirect(url_for('league.leagues'))
    user_leagues = current_user.leagues
    render_template('league.html', user_leagues=user_leagues)