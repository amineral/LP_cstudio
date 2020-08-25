from webapp import app
from webapp.models import User, db


def create_user(username, password1, role='user'):
    with app.app_context():

        new_user = User(username=username, role=role)
        new_user.set_password(password1)

        db.session.add(new_user)
        db.session.commit()
        print(f"Пользователь с именем {new_user.username} создан")

    
if __name__ == '__main__':
    create_user()

    