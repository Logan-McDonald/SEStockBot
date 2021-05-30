from flask import Blueprint, render_template
from flask_login import login_required, current_user

pages = Blueprint('pages', __name__)


@pages.route('/')
def index():
    return render_template('index.html', title='index', user=current_user)
    

@pages.route('/homepage', methods=['GET','POST'])
@login_required
def homepage():
    return render_template('homepage.html', user=current_user)