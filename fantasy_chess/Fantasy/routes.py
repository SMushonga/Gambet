from flask import render_template, request, Blueprint
from fantasy_chess.models import Tournament, Player


fantasy = Blueprint('fantasy', __name__)


@fantasy.route("/")
@fantasy.route("/home")
def home():
    return render_template('home.html')

@fantasy.route("/about")
def about():
    return render_template('about.html', title='About')

@fantasy.route("/tournament/<int: tournament_id>")
def tournament(tournament_id):
    tournament_instance = Tournament.query.get_or_404(tournament_id)
    return render_template('tournament.html', tournament=tournament_instance)

@fantasy.route("/player/<int: player_id>")
def player(player_id):
    player_instance = Player.query.get_or_404(player_id)
    return render_template('player.html', player=player_instance)

@fantasy.route("/schedule")
def schedule():
    upcoming_tournaments = Tournament.query.filter_by(status='Uncommenced').order_by(Tournament.start.asc()).all()
    return render_template('schedule.html', upcoming_tournaments=upcoming_tournaments)