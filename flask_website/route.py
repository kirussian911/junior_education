import sys
from functools import lru_cache

import sqlalchemy

sys.path.append('C:\\Users\\user\\PycharmProjects\\Eqvanta')

import requests
from bs4 import BeautifulSoup as bs
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from database_sql.models import Fbref, Users, db
from markupsafe import Markup
from parsers.parsing_match_data import get_response_match, get_url_match
from sqlalchemy import inspect
from werkzeug.security import check_password_hash, generate_password_hash

admin = Blueprint('main', __name__)


@admin.route('/login')
def login():
    """
    Функция для перехода на страницу авторизации
    """
    return render_template('login.html')


@admin.route('/login', methods=['POST'])
def login_post():
    """
    Функция для получения данных введенных пользователем при авторизации
    """
    email = request.form.get('email')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    remember = True if request.form.get('remember') else False

    # проверяем корректность введенных данных
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('main.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@admin.route('/signup')
def signup():
    """
    Функция для перехода на страницу регистрации пользователя
    """
    return render_template('signup.html')


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    """
    Функция для перехода на главную страницу при logout
    """
    return redirect(url_for('main.index'))


@admin.route('/')
def index():
    """
    Функция сбора и отображения данные на главной странице
    """
    url = 'https://football.kulichki.net/live.htm'
    html_response = requests.get(url).text
    soup = bs(html_response, 'html.parser').find('table')

    url_predict = 'https://football.kulichki.net/prognoz/'
    html_response_predict = requests.get(url_predict).text
    soup_predict = bs(html_response_predict, 'html.parser').find(class_='col2 inl vtop')
    return render_template('index.html', live_stat=Markup(str(soup)), live_stat_predict=Markup(str(soup_predict)))


@admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    matches = []
    res_data_match = {}

    # Получение данных юзера и его запроса
    user_id = current_user.id
    user = db.session.query(Users).filter_by(id=user_id).first()
    res = user.matches_to_dict()

    if request.method == 'POST':
        comp = request.form.get('comp', default='')
        league = request.form.get('league', default='')
        tour = request.form.get('round', default='')
        count_matches = request.form.get('count', default='')
        date = request.form.get('date', default='')
        home_team = request.form.get('squad', default='')
        away_team = request.form.get('opponent', default='')

        if all([tour, league, count_matches]):
            matches = get_matches(league, tour, count_matches)
        try:
            #формируем ссылку на матч
            res_url_match = get_url_match(date_match=date, home_team=home_team, away_team=away_team)

            if res_url_match != '':
                # получаем статистику матча
                res_data_match = get_response_match(res_url_match)
        except TypeError:
            res_data_match = {}

        return render_template('profile.html', res_data_match=res_data_match, name=current_user.name, matches=matches, 
        league=league, round=tour, count=count_matches, date=date, comp=comp, squad=home_team, opponent=away_team, 
        select_matches=res)
    return render_template('profile.html', res_data_match=res_data_match, name=current_user.name, matches=matches, 
    select_matches=res)


@admin.route('/signup', methods=['POST'])
def signup_post():
    """ Функция для регистрации пользователя """

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()

    if user:
        return redirect(url_for('main.signup'))

    # Создание нового юзера и хэширование пароля
    new_user = Users(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # добавление нового юзера в БД
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('main.login'))


def object_as_dict(obj) -> dict:
    "Функция преобразования объекта в словарь"
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


@lru_cache(maxsize=50)
def get_matches(league, tour, count_matches) -> list:
    """Получение данных по запросу в форме Get Matches"""
    
    response = Fbref.query.filter_by(comp=league, round=tour).limit(count_matches).all()
    return [object_as_dict(r) for r in response]


@admin.route('/get_result', methods=['POST'], endpoint='response_new')
@login_required
def get_statistic():
    """Получение статистики конкретного матча в форме Get Result"""
    year = request.form.get('date')
    league = request.form.get('comp')
    home_team = request.form.get('squad')
    away_team = request.form.get('opponent')
    response_new = Fbref.query.filter_by(date=year, comp=league, squad=home_team, opponent=away_team).first()
    if response_new is not None:
        return object_as_dict(response_new)
    else:
        return object_as_dict(response_new)


@admin.route('/add_new_item', methods=['POST'])
@login_required
def add_new_item():
    """Функция для сохранения в БД выбранного матча"""
    # Получение данных юзера и его запроса
    user_id = current_user.id
    match_id = request.form['match_id']

    # Определим в БД матч выбранный юзером
    user = db.session.query(Users).filter_by(id=user_id).first()
    match = db.session.query(Fbref).filter_by(index=match_id).first()
    
    # Сохраняем в базу данных и выводим сообщение
    user.result_select.append(match)
    db.session.add(user)  
    message = "Обновлено в заметках"
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        message='Запись уже есть в заметках'

    # Возвращаем обновленные данные обратно на фронт
    return render_template('message.html', message=message)


@admin.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    """Функция для удаления из БД выбранного матча"""        
    # Получение данных юзера и его запроса
    user_id = current_user.id
    match_id = request.form['match_id']

    # Определим найденные матчи этим юзером
    user = db.session.query(Users).filter_by(id=user_id).first()
    match = db.session.query(Fbref).filter_by(index=match_id).first()
    
    # Удаляем выбранный матч
    user.result_select.remove(match)
    db.session.commit()

    # Вернем обновленные данные обратно на фронт
    return render_template('message.html', message="Матч удален из избранного")
