import requests
from bs4 import BeautifulSoup as bs
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import jsonify
from flask_login import login_user, login_required, current_user, logout_user
from markupsafe import Markup
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash, check_password_hash

from models import Users, Fbref
from models import db

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
        return redirect(url_for('main.login'))

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

    # Создание нового юзера и кэширование пароля
    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # добавление нового юзера в БД
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('main.login'))


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


@admin.route('/match', methods=['GET'])
def match():
    # TODO проверять, если user есть, то выводить, иначе - нет.
    match = Fbref.query.filter_by(squad='Arsenal').first()
    return object_as_dict(match)


@admin.route('/get_matches', methods=['POST'], endpoint='response')
@login_required
def get_matches():
    league = request.form.get('comp')
    tour = request.form.get('round')
    count_matches = request.form.get('count')
    response = Fbref.query.filter_by(comp=league, round=tour).limit(count_matches).all()
    return jsonify(result=[object_as_dict(r) for r in response])


@admin.route('/get_result', methods=['POST'], endpoint='response_new')
@login_required
def get_matches():
    year = request.form.get('date')
    league = request.form.get('comp')
    home_team = request.form.get('squad')
    away_team = request.form.get('opponent')
    response_new = Fbref.query.filter_by(date=year, comp=league, squad=home_team, opponent=away_team).first()
    if response_new is not None:
        return object_as_dict(response_new)
    else:
        # TODO делаем парсер по этому запросу
        pass

