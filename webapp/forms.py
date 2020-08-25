from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, InputRequired, Email, Length, ValidationError
from wtforms.fields.html5 import DateField, DateTimeField

from webapp.models import User


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=30)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Вход')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=30)])
    password1 = PasswordField('password1', validators=[InputRequired(), Length(min=4, max=30)])
    password2 = PasswordField('password2', validators=[InputRequired(), Length(min=4, max=30)])
    submit = SubmitField('Зарегистрировать')

    def validate_username(self, form):
        user = User.query.filter(User.username == self.username.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято. Придумайте другое.')

    def validate_password(self, password1, password2):
        if not password1 == password2:
            raise ValidationError('Пароли должны быть одинаковые')


class CreateProjectForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=4, max=30)])
    description = TextAreaField('description', validators=[Length(min=4, max=256)])
    user = SelectField('user')
    submit = SubmitField('Создать проект')


class CreateArticleForm(FlaskForm):
    title = StringField('title', validators=[InputRequired(), Length(min=2, max=50)])
    text = TextAreaField('text')
    submit = SubmitField('Сохранить статью')


class CreateTaskForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=50)])
    desc = TextAreaField('description', validators=[Length(min=4, max=256)])
    due_date = DateField('due_date')
    user_id = StringField('user_id', validators=[InputRequired(), Length(min=1, max=5)])
    submit = SubmitField('Создать задачу')


class AddUserForm(FlaskForm):
    user = SelectField('user')
    submit = SubmitField('Добавить пользователя')
