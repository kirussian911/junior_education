from flask import Flask
from flask_login import LoginManager
from route import admin
from models import db, Users


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'the random string'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/user/PycharmProjects/Eqvanta/flask_auth_app/project/db.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Users.query.get(int(user_id))

    # регистрирует url адрес
    app.register_blueprint(admin)
    app.run(debug=True)
