from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from fantasy_chess import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Association Tables define many-to-many relationships between two objects 
#db.session.begin_nested()
class User_League(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    old_position = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

class User_Product(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Player_Tournament(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    old_position = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

class Player_Online_Team(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    online_team_id = db.Column(db.Integer, db.ForeignKey('online_team.id'), nullable=False)
    captain = db.Column(db.Boolean,  default=False)

class Player_OTB_Team(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    otb_team_id = db.Column(db.Integer, db.ForeignKey('otb_team.id'), nullable=False)
    captain = db.Column(db.Boolean,  default=False)

class Player_Historic_Online_Teams(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    online_team_id = db.Column(db.Integer, db.ForeignKey('online_team.id'), nullable=False)
    captain = db.Column(db.Boolean,  default=False)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)

class Player_Historic_OTB_Teams(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    otb_team_id = db.Column(db.Integer, db.ForeignKey('otb_team.id'), nullable=False)
    captain = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)

#Tables


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    teamname = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(60), nullable=False, default='Civilian')
    transfer_balance = db.Column(db.Integer, nullable=False, default=200)
    transfers_available = db.Column(db.Integer, nullable=False, default=6)

    account_confirmed = db.Column(db.Boolean)
    account_confirmed_on = db.Column(db.DateTime)

    membership = db.Column(db.String(120), nullable=False, default='Free')
    leagues_created = db.Column(db.Integer, default=0)

    #Lazy=True as one query is generally enough here
    articles = db.relationship('Article', backref='author')
    prizes = db.relationship('Prize', backref='winner')

    online_team = db.relationship('Online_Team', backref='owner', cascade="all, delete")
    otb_team = db.relationship('OTB_Team', backref='owner', cascade="all, delete")

    leagues = db.relationship('User_League', backref='user')
    products = db.relationship('User_Product', backref='user')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email}', '{self.image_file}')"

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    birthdate = db.Column(db.DateTime)
    status = db.Column(db.String(120), default='active')

    Lichess_Username = db.Column(db.String(120))
    Chesscom_Username = db.Column(db.String(120))
    
    online_teams = db.relationship('Player_Online_Team', backref='player')
    otb_teams = db.relationship('Player_OTB_Team', backref='player')

    historic_online_teams = db.relationship('Player_Historic_Online_Teams', backref='player')
    historic_otb_teams = db.relationship('Player_Historic_OTB_Teams', backref='player')

    tournaments = db.relationship('Player_Tournament', backref='player')

class Online_Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    captain_id = db.Column(db.Integer)
    players = db.relationship('Player_Online_Team', backref='online_team', cascade="all, delete")

class Historic_Online_Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    captain_id = db.Column(db.Integer)
    points = db.Column(db.Integer, default=0)
    created = db.Column(db.Datetime)
    players = db.relationship('Player_Historic_Online_Team', backref='otb_team')
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)

class OTB_Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    captain_id = db.Column(db.Integer)
    players = db.relationship('Player_OTB_Team', backref='otb_team', cascade="all, delete")


class Historic_OTB_Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    captain_id = db.Column(db.Integer)
    points = db.Column(db.Integer, default=0)
    created = db.Column(db.Datetime)
    players = db.relationship('Player_Historic_OTB_Team', backref='otb_team')
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    transfer_deadline =  db.Column(db.DateTime)
    tournament_type = db.Column(db.String(120))
    status = db.Column(db.String(120), default='Uncommenced')
    players = db.relationship('Player_Tournament', backref='tournament')
    league = db.relationship('League', backref='tournament')
    otb_teams = db.relationship('Historic_OTB_Teams', backref='tournament')
    online_teams = db.relationship('Historic_Online_Teams', backref='tournament')


class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    league_type = db.Column(db.String(120))
    joining_code = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(120), default='Uncommenced')
    user = db.relationship('User_League', backref='league')
    prizes = db.relationship('Prize', backref='league')
    product = db.relationship('Product', backref='league')
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)

class Prize(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    title = db.Column(db.String(120))
    status = db.Column(db.String(120), default='Unawarded')
    date_awarded = db.Column(db.DateTime)
    value = db.Column(db.Integer)
    winner_id = db.Column(db.Integer, db.ForeignKey('winner.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Article('{self.title}', '{self.date_posted}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    cost = db.Column(db.Integer)
    subscription = db.Column(db.Boolean, nullable=False, default=False)
    stripe_price_id = db.Column(db.String(120))
    product_id = db.Column(db.String(120))
    period = db.Column(db.String(120), nullable=True)
    user = db.relationship('User_Product', backref='product')
    league_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

