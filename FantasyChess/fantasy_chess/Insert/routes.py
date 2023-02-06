from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db
import stripe
from fantasy_chess.config import Config
from fantasy_chess.Insert.forms import Tournament_Form, Player_Form, News_Form
from fantasy_chess.models import User, Tournament, League, Online_Team, OTB_Team, Player_Online_Team, Player_OTB_Team, Player, Historic_Online_Teams, Historic_OTB_Teams
from datetime import datetime, time, date
from fantasy_chess.League.functions import create_league_function
from fantasy_chess.Payments.functions import create_product_for_league
insert = Blueprint('insert', __name__)

stripe.api_key= Config.STRIPE_SECRET_KEY

@insert.route('/insert_tournament', methods=['GET', 'POST'])
def insert_tournament():
    form = Tournament_Form()
    if form.validate_on_submit():
        transfer_deadline = datetime.combine(form.Start.data.date(), time())
        new_tournament = Tournament(title=form.Title.data, start = form.Start.data, end= form.End.data, tournament_type=form.Tournament_Type.data)
        db.session.add(new_tournament)
        create_league_function(title=form.Title.data, league_start=form.Start.data, league_end=form.End.data, user=current_user)

        #A more robust query needs to be inserted here
        league = League.query.filter_by(title=form.Title.data, league_start=form.Start.data).first()
        league.tournament = new_tournament

        try:
            if create_product_for_league(league.id, cost=500):
                db.session.commit()
                return redirect(url_for('insert.insert_player_tournament', tournament_id=new_tournament.id))
            else:
                db.session.rollback()
                flash(f'We could not create the tournament entry for the tournament, please re-enter this information', 'failure')
                return redirect(url_for('insert.insert_tournament'))
        except Exception as e:
            db.session.rollback()
            flash(f'{e} was the error, please try again,', 'failure')
            return redirect(url_for('insert.insert_tournament'))
    return render_template('insert_tournament.html', form=form)

@insert.route('/insert_player', methods=['GET'])
def insert_player():
    form = Player_Form()
    if form.validate_on_submit():
        player = Player(name=form.Name.data, rating=form.Rating.data, cost=form.Cost.data, birthdate=form.Birthdate.data, Lichess_Username=form.Lichess_Username.data, Chesscom_Username=form.Chesscom_Username.data)
        db.session.add(player)
        db.session.commit()
    return render_template('insert_player.html', form=form)

@insert.route('/insert_player_tournament/<tournament_id>', methods=['GET'])
def insert_player_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.all()
    if request.method == 'POST':
        return redirect(url_for('home'))
    render_template('insert_player_tournament.html', players=players)

@insert.route('/insert_news', methods=['GET'])
def insert_news():
    form = News_Form()
    if form.validate_on_submit():
        pass
    return render_template('insert_news.html', form=form)


#Give out prizes 