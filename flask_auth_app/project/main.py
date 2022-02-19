from flask_login import LoginManager
from route import admin
from models import db, Users
from config import app


if __name__ == '__main__':
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
