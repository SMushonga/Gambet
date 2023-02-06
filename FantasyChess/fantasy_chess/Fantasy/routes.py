from flask import render_template, request, Blueprint


fantasy = Blueprint('fantasy', __name__)


@fantasy.route("/")
@fantasy.route("/home")
def home():
    return render_template('home.html')

@fantasy.route("/about")
def about():
    return render_template('about.html', title='About')