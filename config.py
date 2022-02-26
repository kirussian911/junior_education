from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'the random string'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/user/PycharmProjects/Eqvanta/flask_auth_app/project/db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

path_to_dbase = r'/db.sqlite'
table_name = 'fbref'