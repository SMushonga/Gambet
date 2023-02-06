from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db
from fantasy_chess.Teams.functions import make_transfer
from fantasy_chess.models import Tournament,  Player, Historic_Online_Teams, Historic_OTB_Teams, Article

teams = Blueprint('teams', __name__)

@teams.route('/my_team', methods=['GET'])
def my_team():
    #If out user does not have a team yet, they should make one before viewing subsequent pages
    if not current_user.online_team or current_user.otb_team:
        return redirect('teams.transfer')

    next_fixture = Tournament.query.filter_by(status='Uncommenced').order_by(Tournament.start).first()
    user_leagues = current_user.leagues
    prizes = current_user.prizes
    articles = Article.query.order_by(Article.date_posted.desc()).limit(5).all()

    if request.method=='POST':
        #placeholder, captain_id is in the request
        captain_id = request.get_json()
        #Teams are only 3 people so looping is not too inefficient - consider querying just for the old captain and new captain
        for i in range(3):
            if current_user.online_team.players[i].player_id == captain_id:
                current_user.online_team.players[i].captain = True
            elif current_user.otb_team.players[i].player_id == captain_id:
                current_user.otb_team.players[i].captain = True
            else:
                current_user.online_team.players[i].captain = False
                current_user.otb_team.players[i].captain = False

    return render_template('my_team', next_fixture=next_fixture, user_leagues=user_leagues, otb_team=current_user.otb_team, online_team=current_user.online_team, prizes=prizes, articles=articles)

@teams.route('/transfers', methods=['GET', 'POST'])
def transfer():
    if not current_user.otb_team or not current_user.online_team:
        return redirect(url_for('teams.create_team'))
    #Query current team 
    online_team_ids = [player.player_id for player in current_user.online_team.players]
    otb_team_ids = [player.player_id for player in current_user.otb_team.players]
    
    players = Player.query.filter_by(status='active').all()
    if request.method=='POST':
        if make_transfer(user=current_user, new_team_online_ids = request, new_team_otb_ids=request):
            flash('Transfer successful', 'success')

    return render_template('transfers.html', players=players, online_team_ids=online_team_ids, otb_team_ids=otb_team_ids, online_team=current_user.online_team.players, otb_team=current_user.otb_team.players, balance = current_user.transfer_balance)

@teams.route('/create_team', methods=['GET', 'POST'])
def create_team():
    players = Player.query.filter_by(status='active').all()
    return render_template('transfers.html', players=players, balance = current_user.transfer_balance)

@teams.route('/my_points/<tournament_id>', methods=['GET', 'POST'])
def my_points(tournament_id):
    if tournament_id==0:
        tournament = Tournament.query.filter_by(status='in progress').order_by(Tournament.start).first()
    tournament = Tournament.query.get_or_404(tournament_id)
    online_team = Historic_Online_Teams.query.filter_by(owner_id=current_user.id, tournament_id=tournament_id).first()
    otb_team = Historic_OTB_Teams.query.filter_by(owner_id=current_user, tournament_id=tournament_id).first()

    if not (online_team or otb_team):
        flash(f'This tournament is not yet started, redirected to my team')
        return redirect(url_for('teams.my_team'))
    return render_template('my_points.html', online_team=online_team, otb_team=otb_team, tournament=tournament)

    