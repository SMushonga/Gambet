from fantasy_chess.models import User, Online_Team, OTB_Team, Player, Player_Online_Team, Player_OTB_Team
from fantasy_chess import db

def create_team(user, team_online_ids, team_otb_ids):

    if len(set(team_online_ids + team_otb_ids)) != 6 or len(team_online_ids)!=3 or len(team_otb_ids)!=3 or user.online_team or user.otb_team:
        return None

    new_online_team = Player.query.filter(Player.id._in(team_online_ids)).all()
    new_otb_team = Player.query.filter(Player.id._in(team_otb_ids)).all()

    new_team = new_online_team + new_otb_team
    if len(new_team) != 6: return None
    
    transfer_balance = user.transfer_balance
    for player in new_team: transfer_balance += player.cost

    if transfer_balance > 0:
        user.transfer_balance = transfer_balance
    else:
        return None

    for player in new_online_team: 
        player_addition = Player_Online_Team(online_team=user.online_team, player=player)
        db.session.add(player_addition)
    for player in new_otb_team:
        player_addition = Player_OTB_Team(otb_team=user.otb_team, player=player)
        db.session.add(player_addition)
    db.session.commit()
    return True

def make_transfer(user, new_team_online_ids, new_team_otb_ids):
    #Check if the user's otb and online team, are distinct and only three entries lng
    if len(set(new_team_online_ids + new_team_otb_ids)) != 6 or len(new_team_online_ids)!=3 or len(new_team_otb_ids)!=3:
        return None

    online_team_ids = [player.player_id for player in user.online_team.players]
    otb_team_ids = [player.player_id for player in user.otb.players]

    #Check if the user has the available transfers to complete this transaction
    num_transfers = 12 - len(set(online_team_ids + new_team_online_ids + otb_team_ids + new_team_otb_ids))
    if num_transfers > user.transfers_available or num_transfers == 0:
        return None
    #Sell the old players and check if the user can afford the transfer 
    new_online_team = Player.query.filter(Player.id._in(new_team_online_ids)).all()
    new_otb_team = Player.query.filter(Player.id._in(new_team_otb_ids)).all()

    new_team = new_online_team + new_otb_team
    if len(new_team) != 6: return None
    old_team = user.online_team + user.otb_team

    transfer_balance = user.transfer_balance 
    for player in new_team: transfer_balance += player.cost
    for player in old_team: transfer_balance -= player.cost 
    
    if transfer_balance > 0:
        user.transfer_balance = transfer_balance
    else:
        return None
    

    Player_Online_Team.query.filter(Player_Online_Team.id._in(online_team_ids)).delete()
    Player_OTB_Team.query.filter_by(Player_OTB_Team.id._in(otb_team_ids)).delete()

    #Buy new players
    for player in new_online_team: 
        player_addition = Player_Online_Team(online_team=user.online_team, player=player)
        db.session.add(player_addition)
    for player in new_otb_team:
        player_addition = Player_OTB_Team(otb_team=user.otb_team, player=player)
        db.session.add(player_addition)
    #Deduct the transfers made from transfers available
    user.transfers_available -= num_transfers
    db.session.commit()
    return True
    