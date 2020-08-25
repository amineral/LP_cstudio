from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, logout_user, login_user, login_required

from webapp import app
from webapp.forms import LoginForm, RegisterForm, CreateProjectForm, CreateArticleForm, CreateTaskForm, AddUserForm
from webapp.models import User, Article, Project, Task, get_trello_task


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return render_template('index.html', page_title='Login')


@app.route('/home')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    articles = Article.query.filter(Article.users.any(id=current_user.id)).order_by(Article.created_date.desc()).all()
    projects = Project.query.filter(Project.users.any(id=current_user.id)).order_by(Project.created_date.desc()).all()
    tasks = Task.query.filter(Task.user_id == current_user.id).all()
    return render_template('home.html', articles=articles, projects=projects, tasks=tasks)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if current_user.is_authenticated:
        user = User.query.filter(User.id == current_user.id).first()
        return render_template('profile.html', user=user)
    return redirect(url_for('index'))

@app.route('/settings', methods=["GET", "POST"])
def profile_settings():
    user = User.query.filter(User.id == current_user.id).first()
    new_email = request.form.get("new_email")
    new_first_name = request.form.get("new_first_name")
    new_second_name = request.form.get("new_second_name")
    new_third_name = request.form.get("new_third_name")
    email = User.query.filter(User.email == new_email).count()
    if new_email:
        if email:
            flash("Пользователь с таким email уже существует")
        else:
            user.set_email(new_email)
        return render_template("profile_settings.html", user=user)
    if new_first_name:
        user.set_name(new_first_name, 'first')
    if new_second_name:
        user.set_name(new_second_name, 'second')
    if new_third_name:
        user.set_name(new_third_name, 'third')
    return render_template("profile_settings.html", user=user)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    return render_template('login.html', page_title='Авторизация', form=login_form)


@app.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Неправильное имя или пароль')
        return redirect(url_for('login'))
    else:
        flash('Что-то пошло не так')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    flash('Разлогинено')
    return redirect(url_for('index'))


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    reg_form = RegisterForm()
    return render_template('reg.html', page_title='Регистрация', form=reg_form)


@app.route('/process-reg', methods=['GET', 'POST'])
def process_reg():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        User.create_user(username=form.username.data, password1=form.password1.data)
        flash("Вы успешно зарегистрировались")
        return redirect(url_for('login'))


@app.route('/create-project', methods=['GET', 'POST'])
def process_create_project():
    if current_user.role == 'admin':
        users = User.query.all()
        user_list = [user.username for user in users if not user == current_user]
        form = CreateProjectForm()
        form.user.choices = user_list
        if request.method == 'POST':
            user_id = User.query.filter(User.username == form.user.data).first().id
            Project.create(name=form.name.data, description=form.description.data, user_id=user_id)
            flash(f"Проект создан")
            return redirect(url_for('home'))
        else:
            return render_template('create-project.html', page_title='Создать проект', form=form)
    else:
        flash(f"Только админ может создавать проекты")
        return redirect(url_for('home'))


@app.route('/projects/<int:project_id>/add-user', methods=['GET', 'POST'])
def add_user(project_id):
    if current_user.role == 'admin':
        users = User.query.all()
        project_users = Project.query.filter(Project.id == project_id).first().users
        user_list = [user.username for user in users if not user in project_users]
        form = AddUserForm()
        form.user.choices = user_list
        if request.method == 'POST':
            user_id = User.query.filter(User.username == form.user.data).first().id
            Project.query.filter(Project.id == project_id).first().add_user(user_id)
            flash(f"Пользователь добавлен")
            return redirect(url_for('show_project', project_id=project_id))
        else:
            return render_template('add-user.html', page_title='Добавить пользователя', form=form, project_id=project_id)
    else:
        flash(f"Только админ может добавлять пользователей")
        return redirect(url_for('home'))


@app.route('/projects/<int:project_id>/delete-project', methods=['GET', 'POST'])
def process_delete_project(project_id):
    if current_user.role == 'admin':
        Project.query.filter(Project.id == project_id).first().delete(project_id)
        flash("Проект удален")
        return redirect(url_for('home'))
    else:
        flash(f"Только админ может удалять проекты")
        return redirect(url_for('home'))


@app.route('/create-article', methods=['GET', 'POST'])
def process_create_article():
    form = CreateArticleForm()
    if request.method == 'POST':
        Article.create(title=form.title.data, text=form.text.data, author=current_user.username)
        flash("Статья создана")
        return redirect(url_for('home'))
    else:
        return render_template('create-article.html', page_title='Написать статью', form=form)


@app.route('/articles/<int:article_id>', methods=['GET', 'POST'])
def show_article(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    return render_template('show-article.html', article=article)


@app.route('/projects/<int:project_id>', methods=['GET', 'POST'])
def show_project(project_id):
    project = Project.query.filter(Project.id == project_id).first()
    tasks = project.tasks
    todo = [task for task in tasks if task.get_status(task.trello_id) == "в планах"]
    inprocess = [task for task in tasks if task.get_status(task.trello_id) == "в работе"]
    done = [task for task in tasks if task.get_status(task.trello_id) == "готово"]
    return render_template('show-project.html', project=project, todo=todo, inprocess=inprocess, done=done)


@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
def show_task(task_id):
    id = Task.query.filter(Task.id == task_id).first().trello_id
    trello_task = get_trello_task(id)
    name, desc, due, list_id = trello_task
    task = Task.query.filter(Task.id == task_id).first()
    status = task.get_status(id)
    project = Project.query.filter(Project.id == task.project_id).first()
    username = User.query.filter(User.id == task.user_id).first().username
    return render_template('show-task.html', name=name, username=username, desc=desc, due=due, status=status, project=project)


@app.route('/projects/<int:project_id>/<list_id>/create-task', methods=['GET', 'POST'])
def process_create_task(project_id, list_id):
    form = CreateTaskForm()
    if request.method == 'POST':
        Task.create(name=form.name.data, desc=form.desc.data, due=form.due_date.data, list_id=list_id, user_id=form.user_id.data, project_id=project_id)
        flash("Задача создана")
        return redirect(url_for('home'))
    return render_template('create-task.html', page_title='Новая задача', form=form, list_id=list_id, project_id=project_id)