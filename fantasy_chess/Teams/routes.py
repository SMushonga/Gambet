from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db
from fantasy_chess.Teams.functions import make_transfer
from fantasy_chess.models import Tournament,  Player, Historic_Online_Teams, Historic_OTB_Teams, Article
import json

teams = Blueprint('teams', __name__)

@teams.route('/my_team', methods=['GET'])
def my_team():
    #If out user does not have a team yet, they should make one before viewing their team
    if not current_user.online_team or current_user.otb_team:
        return redirect('teams.create_team')
    
    #After a user saves their captain, the frontend sends a post request with the captains data
    if request.method=='POST':
        captain_id_string = request.get_json()
        captain_id_dictionary = json.loads(captain_id_string)
        #We set both teams' captains to the chosen captain, but the captain bonus is considered once in the scoring function later.
        if Player.query.get(int(captain_id_dictionary['captain'])):
            current_user.online_team.captain_id = int(captain_id_dictionary['captain'])
            current_user.otb_team.captain_id = int(captain_id_dictionary['captain'])
        db.session.commit()

        #We send back a success signal to the frontend that'll notify the user
        results = {'captain_changed': 'true'}
        return jsonify(results)
    
    next_fixture = Tournament.query.filter_by(status='Uncommenced').order_by(Tournament.start).first()
    user_leagues = current_user.leagues
    prizes = current_user.prizes
    articles = Article.query.order_by(Article.date_posted.desc()).limit(5).all()
    captain_id = current_user.online_team.captain_id 

    return render_template('my_team', next_fixture=next_fixture, user_leagues=user_leagues, otb_team=current_user.otb_team, online_team=current_user.online_team, prizes=prizes, articles=articles, captain_id=captain_id)

@teams.route('/transfers', methods=['GET', 'POST'])
def transfer():
    if not current_user.otb_team or not current_user.online_team:
        return redirect(url_for('teams.create_team'))
    #Query current team 
    online_team_ids = [player.player_id for player in current_user.online_team.players]
    otb_team_ids = [player.player_id for player in current_user.otb_team.players]
    
    players = Player.query.filter_by(status='active').all()
    if request.method=='POST':
        transfers_string = request.get_json()
        transfers_dictionary = json.loads(transfers_string)

        new_otb_team_ids = list(transfers_dictionary['otb'])
        new_online_team_ids = list(transfers_dictionary['online'])

        if make_transfer(user=current_user, new_team_online_ids = new_online_team_ids, new_team_otb_ids=new_otb_team_ids):
            results = {'transfer_successful': 'true'}
            return jsonify(results)
        else:
            results = {'transfer_successful': 'false'}
            return jsonify(results)

    return render_template('transfers.html', players=players, online_team_ids=online_team_ids, otb_team_ids=otb_team_ids, online_team=current_user.online_team.players, otb_team=current_user.otb_team.players, balance = current_user.transfer_balance)

@teams.route('/create_team', methods=['GET', 'POST'])
def create_team():
    players = Player.query.filter_by(status='active').all()
    return render_template('transfers.html', players=players, balance = current_user.transfer_balance)

@teams.route('/my_points/<tournament_id>', methods=['GET', 'POST'])
def my_points(tournament_id):
    if tournament_id==0:
        tournament = Tournament.query.filter_by(status='in progress').order_by(Tournament.start.desc()).first()
    else:
        tournament = Tournament.query.get_or_404(tournament_id)

    online_team = Historic_Online_Teams.query.filter_by(owner_id=current_user.id, tournament_id=tournament_id).first()
    otb_team = Historic_OTB_Teams.query.filter_by(owner_id=current_user.id, tournament_id=tournament_id).first()
    if not (online_team or otb_team):
        flash(f'This tournament has either not yet started, or you did not have a team for this tournament. Redirected to my_team')
        return redirect(url_for('teams.my_team'))
    
    user_leagues = current_user.leagues
    #Impossible to not have a league as creating a team enters you into league with all players 
    prizes = tournament.league.prizes
    return render_template('my_points.html', online_team=online_team, otb_team=otb_team, tournament=tournament, prizes=prizes, user_leagues=user_leagues)

    