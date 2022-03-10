from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, inspect

from config import app

db = SQLAlchemy(app=app)


# Создание промежуточной таблицы для сохранения данных: id user и сохраненные id матчей
association_table = db.Table(
    'users_select', db.Model.metadata,
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('match_id', db.Integer(), db.ForeignKey('fbref.index')),
    UniqueConstraint('user_id', 'match_id', name='uix_1'))


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # Для получения доступа к связанным объектам
    result_select = db.relationship('Fbref', secondary=association_table, backref=db.backref('fbref', lazy='dynamic'))
    
    def matches_to_dict(self) -> list:
        "Функция преобразования объекта в список словарей"
        return [result.transformation_to_dict() for result in self.result_select]


class Fbref(db.Model):
    __tablename__ = 'fbref'
    index = db.Column(db.Integer, primary_key=True, unique=False)
    squad = db.Column(db.String(100))
    date = db.Column(db.String(100))
    comp = db.Column(db.String(100))
    round = db.Column(db.String(100))
    dayofweek = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    result = db.Column(db.String(100))
    goals_for = db.Column(db.Integer)
    goals_against = db.Column(db.Integer)
    opponent = db.Column(db.String(100))
    possession = db.Column(db.Integer)
    attendance = db.Column(db.Integer)
    captain = db.Column(db.String(100))
    formation = db.Column(db.String(100))
    referee = db.Column(db.String(100))
    
    def transformation_to_dict(self) -> dict:
        "Функция преобразования объекта в словарь"
        return{c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


db.create_all()
db.session.commit()

users = Users.query.all()
