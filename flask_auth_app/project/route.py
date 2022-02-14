from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users
from models import db
from flask_login import login_user, login_required, current_user, logout_user
import requests
from bs4 import BeautifulSoup as bs
from markupsafe import Markup


admin = Blueprint('main', __name__)


@admin.route('/login')
def login():
    return render_template('login.html')


@admin.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()

    remember = True if request.form.get('remember') else False

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('main.login'))  # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@admin.route('/signup')
def signup():
    return render_template('signup.html')


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@admin.route('/')
def index():
    url = 'https://football.kulichki.net/live.htm'
    html_response = requests.get(url).text
    soup = bs(html_response, 'html.parser').find('table')

    url_predict = 'https://football.kulichki.net/prognoz/'
    html_response_predict = requests.get(url_predict).text
    soup_predict = bs(html_response_predict, 'html.parser').find(class_='col2 inl vtop')
    return render_template('index.html', live_stat=Markup(str(soup)), live_stat_predict=Markup(str(soup_predict)))


@admin.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@admin.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = Users.query.filter_by(email=email).first()

    if user:
        return redirect(url_for('main.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('main.login'))
