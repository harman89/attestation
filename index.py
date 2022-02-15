import datetime
import random
import string
import xml.etree.ElementTree as ET
from os.path import dirname, join, realpath,exists

import flask
from flask import render_template, request, jsonify, flash, send_from_directory, Flask, abort, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from model import db, app, User, Grade, Position

db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = '/'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

def insert_admin():
    if not db.session.query(User).filter(User.login == "admin").first():
        user = User(login="admin", first_name="admin", last_name="admin", mid_name="admin", email="admin@admin.ru",start_date=datetime.datetime.now(),admin_flg=True,can_approve_flg=True,active_flg=True)
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()

def insert_position():
    pos = Position(name="Разрабочик Siebel")
    db.session.add(pos)
    db.session.commit()

def insert_grade():
    if not db.session.query(Grade).filter(Grade.name == "2").first():
        pos = db.session.query(Position).filter(Position.id == 1).first()
        grade = Grade(name="2",description="Второй грейд", position=pos)
        db.session.add(grade)
        db.session.commit()

#вставка админской записи, потом убрать!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
insert_admin()
insert_grade()


@app.route("/generate_invite_code", methods=['POST'])
@login_required
def generate_invite_code():
    flash("test")
    choice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in [i for i in list(string.ascii_uppercase)]:
        choice.append(i)
    code = ""
    for i in range(6):
        code += str(random.choice(choice))
    #db.session.add(InviteCode(text=code))
    db.session.commit()
    return render_template('sample.html')


@app.route('/')
def index(message=""):
    if current_user.is_authenticated:
        return redirect('/home')
    else:
        return render_template('auth.html', message=message)

@app.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('main.html', user = current_user)
    else:
        return redirect('/')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if flask.request.method == 'POST':
        if db.session.query(InviteCode).filter(InviteCode.text == request.form.get("invite_code")).first():
            user = User(username=request.form.get("username"), surname=request.form.get("surname"),
                        name=request.form.get("name"),
                        email=request.form.get("email"))
            user.set_password(request.form.get("password"))
            db.session.add(user)
            db.session.commit()
            return render_template('auth.html', message="Успешная регистрация")
        else:
            return render_template('auth.html', message="Неверный код приглашения")
    else:
        return render_template('registration.html')


@app.route('/exit')
@login_required
def logout():
    logout_user()
    return render_template('auth.html')


@app.route('/skills_add')
@login_required
def add_skill():
    #print("meow")
    if current_user.admin_flg:
        return render_template('skills_add.html', user = current_user, grades = db.session.query(Grade))
    else:
        return redirect('/home')

@app.route('/auth', methods=['GET', 'POST'])
def login():
    login = request.form.get("user")
    password = request.form.get("pass")
    user = db.session.query(User).filter(User.login == login).first()
    if user and user.check_password(password):
        login_user(user, remember=True)
        db.session.add(user)
        db.session.commit()
        #return render_template('main.html', first_name= user.first_name, last_name= user.last_name)
        #return redirect(url_for('home', first_name= user.first_name, last_name= user.last_name))
        return redirect('/home')
    else:
        print("error, net usera")
        return render_template("auth.html", message="Ошибка авторизации")

@app.route('/grade_add', methods=['GET', 'POST'])
def gradeAdd():
    gradeName = request.form.get("name")
    gradeDesk = request.form.get("desk")
    #пока что гриды добавляются только для одного Position (Siebel разработчик)
    gradePosition = db.session.query(Position).filter(Position.id == 1).first()
    grade = Grade(name=gradeName,description=gradeDesk, position=gradePosition)
    db.session.add(grade)
    db.session.commit()
    return redirect('/skills_add')
