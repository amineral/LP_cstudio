import os

#получаем путь к нашему файлу
basedir = os.path.abspath(os.path.dirname(__file__))

#указываем где хотим, чтобы находился файл cstudio.db
#директория запускаемого файла(basedir) и на одну директорию выше(..)
# sqlite:/// нужен для того, чтоьбы дать понять, какой тип бд мы хотим использовать
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "..", "cstudio.db")
# sqlite:/// нужен для того, чтоьбы дать понять, какой тип бд мы хотим использовать
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = '784ggfrdjbdf9wfidsc8e'

TRELLO_TOKEN = 'b3c0529ae2674523d1f6f178732385cfff48113e3881275039bd8625fc75a874'
TRELLO_KEY = '6c29036b025c7af127e7e32181d2d995'
TRELLO_OAUTH = 'a6d2239e4ec39a1550d328bffdf69b09e89e9bf3c57defb66362795d39aa3f6e'


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'