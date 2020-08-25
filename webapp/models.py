from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from trello import *

db = SQLAlchemy()


user_project = db.Table('user_project',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')))


user_article = db.Table('user_article',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id', ondelete='CASCADE')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    second_name = db.Column(db.String(50), nullable=True)
    third_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')
    projects = db.relationship('Project', secondary=user_project, back_populates='users')
    articles = db.relationship('Article', secondary=user_article, back_populates='users')
    tasks = db.relationship('Task', backref='user')

    def __repr__(self):
        return f'{self.username}'

    @classmethod
    def create_user(self, username, password1):
        self.new_user = User(username=username)
        self.new_user.set_password(password1)
        db.session.add(self.new_user)
        db.session.commit()

    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_email(self, email):
        self.email = email
        db.session.add(self)
        db.session.commit()
    
    def set_name(self, name, name_number):
        if name_number == 'first':
            self.first_name = name
        elif name_number == 'second':
            self.second_name = name
        elif name_number == 'third':
            self.third_name = name
        db.session.add(self)
        db.session.commit()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.UnicodeText(256))
    trello_id = db.Column(db.Integer, nullable=False)
    planner_id = db.Column(db.Integer, nullable=False, default=1)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    todo_id = db.Column(db.String(20), nullable=True, default=1)
    inprocess_id = db.Column(db.String(20), nullable=True, default=1)
    done_id = db.Column(db.String(20), nullable=True, default=1)
    users = db.relationship('User', secondary=user_project, back_populates='projects')
    tasks = db.relationship('Task', backref='project')


    def __repr__(self):
        return f'<Project: {self.name}, id: {self.id}>'

    @classmethod
    def create(self, name, description, user_id):
        trello_id = get_trello_id(name)
        todo_id, inprocess_id, done_id = get_trello_lists(trello_id)
        self.new_project = Project(name=name, description=description, trello_id=trello_id, planner_id=1,
                                   todo_id=todo_id, inprocess_id=inprocess_id, done_id=done_id)
        self.new_project.users.append(current_user)
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            self.new_project.users.append(user)
        db.session.add(self.new_project)
        db.session.commit()

    @classmethod
    def delete(self, project_id):
        trello_id = self.query.filter(self.id == project_id).first().trello_id
        delete_trello_board(id=trello_id)
        self.query.filter_by(id=project_id).delete()
        db.session.commit()

    @classmethod
    def add_user(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        project = Project.query.filter(Project.id == self.id).first()
        project.users.append(user)
        db.session.commit()


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.UnicodeText)
    author = db.Column(db.String(32), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', secondary=user_article, back_populates='articles')

    @classmethod
    def create(self, title, text, author):
        self.new_article = Article(title=title, text=text, author=author)
        db.session.add(self.new_article)
        current_user.articles.append(self.new_article)
        db.session.commit()

    @classmethod
    def delete(self, article_id):
        self.query.filter_by(id=article_id).delete()
        db.session.commit()

    def __repr__(self):
        return f"<{self.name}, id: {self.id}>"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    trello_id = db.Column(db.Integer, nullable=False)

    # description = db.Column(db.String(250))
    # created_date = db.Column(db.DateTime, default=datetime.utcnow)
    # due_date = db.Column(db.DateTime)
    # list_id = db.Column(db.String(25), nullable=False)   #list_id привязывает таск к опред.списку (статусу) на доске

    @classmethod
    def create(self, name, desc, due, list_id, user_id, project_id):
        if not due is None:
            due = due.isoformat()
        trello_id = add_trello_task(list_id, name, desc, due)
        self.new_task = Task(user_id=user_id, trello_id=trello_id, project_id=project_id, name=name)
        project = Project.query.filter(Project.id == project_id).first()
        project.tasks.append(self.new_task)
        user = User.query.filter(User.id == user_id).first()
        user.tasks.append(self.new_task)
        db.session.add(self.new_task)
        db.session.commit()

    @classmethod
    def get_status(self, trello_id):
        task = get_trello_task(trello_id)
        list_id = task[3]
        project = Project.query.filter(Project.id == self.project_id).first()
        todo_id = project.todo_id
        inprocess_id = project.inprocess_id
        done_id = project.done_id

        if list_id == todo_id:
            status = 'в планах'
        elif list_id == inprocess_id:
            status = 'в работе'
        elif list_id == done_id:
            status = 'готово'

        return status

    def __repr__(self):
        return f"<{self.name}, id: {self.id}>"