from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'the random string'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/user/PycharmProjects/Eqvanta/flask_db.db"
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

path_to_dbase = 'C:\\Users\\user\\PycharmProjects\\Eqvanta\\flask_db.db'
table_name = 'fbref'
