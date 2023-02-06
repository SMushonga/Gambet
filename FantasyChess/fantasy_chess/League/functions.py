from fantasy_chess.models import League, User, User_League
from fantasy_chess import db
import random, string

def join_league_function(code, user):
    league = League.query.filter_by(joining_code=code).first()
    if league:
        user_league = User_League(league=league, user=user)
        db.session.add(user_league)
        db.session.commit()
        return True
    return False


def create_league_function(title, league_start, league_end, user):
    #Firstly we check whether this user can create a league
    if user.leagues_created > 3 and user.membership=='Free' and user.role=='Civilian':
        return False

    joining_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    #We can't have duplicate codes, we ensure that by performing a quick search
    unique_code_check = League.query.filter_by(joining_code=joining_code).first()
    if unique_code_check:
        #We iterate the function again
        create_league_function(title, league_start, league_end, user)
    else:
        new_league = League(title=title, start=league_start, end=league_end, joining_code=joining_code)
        user_league = User_League(league=new_league, user=user)
        db.session.add(new_league)
        db.session.add(user_league)

        user.leagues_created += 1
        db.session.commit()
        return True
