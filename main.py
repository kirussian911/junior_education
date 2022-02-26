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
        return Users.query.get(int(user_id))

    app.register_blueprint(admin)
    app.run(debug=True)
