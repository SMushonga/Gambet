from fantasy_chess.models import Tournament, Online_Team, OTB_Team, Player_Tournament, League, User_League, Player_Historic_Online_Teams, Player_Online_Team, Historic_Online_Teams, Historic_OTB_Teams,Player_Historic_OTB_Teams
from fantasy_chess import db
from datetime import datetime, timedelta

accomplishments = {'attribute' : 8, 'attribute_2': 9}

def update_tournaments(scores):
    started_tournaments_update = Tournament.query.filter_by(datetime.utcnow() + timedelta(days=1) > transfer_deadline > datetime.utcnow()).update(status='in progress')
    finished_tournaments_update = Tournament.query.filter_by(status='in progress', end > datetime.utcnow()).update(status='finished')


#Points Capture happens to every ongoing tournament, where the current points from the previous round are calculated at theend of the day
def points_capture(updates_dictionary, tournament_id):
    #Dictionary is formatted like {'id':{'attribute_name':count, 'attribute_name':count...}}
    
    tournament_player = Player_Tournament.query.filter_by(tournament_id=tournament_id).first()
    for association in tournament_player:
        achievements = updates_dictionary[association.player_id]
        player_latest_points_haul = 0
        for achievement in achievements:
            #Calculate update 
            player_latest_points_haul += accomplishments[achievement]
            #This is so we can see how they achieved the points
            setattr(association, achievement, getattr(association, achievement) + achievements[achievement])
        #We update the points scored by each player for their respective teams

        #Historic_Online_Teams.query.join(Historic_Online_Teams.players)\
            #.filter_by(tournament_id=association.tournament_id, player_id=association.player_id).update({Historic_Online_Teams.points:Historic_Online_Teams.points + player_latest_points_haul})
        Historic_Online_Teams.query.join(Historic_Online_Teams.players)\
            .join(User_League, Historic_Online_Teams.owner_id==User_League.user_id)\
            .filter_by(tournament_id=association.tournament_id, player_id=association.player_id).update({User_League.points:User_League.points + player_latest_points_haul, Historic_Online_Teams.points:Historic_Online_Teams.points + player_latest_points_haul})

    db.session.commit()   #League is still open, you own the player 
#Calculate how many points the player is getting ?


def league_update():
    #Closing Leagues
    League.query.filter_by(status='in progress', end> datetime.utcnow() + timedelta(days=1)).update({League.status:'finished'})
    #Opening Leagues
    League.query.filter_by(status='Uncommenced', start > datetime.utcnow() + timedelta(days=1)).update({League.status:'in progress'})
    db.session.commit()

def capture_teams(tournament_id):
    #When the transfer deadline of a tournament is reached, this funtion captures every users team
    tournament= Tournament.query.get(id=tournament_id)
    if tournament.tournament_type=='online':
        online_teams = Online_Team.query.all()
        for team in online_teams:
            team_for_tournament = Historic_Online_Teams(owner=team.owner, captain_id=team.captain_id, created=datetime.utcnow, tournament=tournament)
            db.session.add(team_for_tournament)
            for player in team.players:
                player_historic = Player_Historic_Online_Teams(player=player.player, online_team=team_for_tournament, user_id=team.owner_id)
                db.session.add(player_historic)
        db.session.commit()
        return True
    elif tournament.tournament_type=='otb':
        otb_teams = OTB_Team.query.all()
        for team in otb_teams:
            team_for_tournament = Historic_OTB_Teams(owner=team.owner, captain_id=team.captain_id, created=datetime.utcnow, tournament=tournament)
            db.session.add(team_for_tournament)
            for player in team.players:
                player_historic = Player_Historic_OTB_Teams(player=player.player, online_team=team_for_tournament, user_id=team.owner_id)
                db.session.add(player_historic)
        db.session.commit()
        return True
    else:
        return False

