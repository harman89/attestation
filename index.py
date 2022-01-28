import datetime
import random
import string
import xml.etree.ElementTree as ET
from os.path import dirname, join, realpath,exists

import flask
from flask import render_template, request, jsonify, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from model import db, app, User

db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = '/'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


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
        return render_template('sample.html')
    else:
        return render_template('auth.html', message=message)


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
    print("meow")


@app.route('/auth', methods=['GET', 'POST'])
def login():
    login = request.form.get("user")
    password = request.form.get("pass")
    user = db.session.query(User).filter(User.login == login).first()
    if user and user.check_password(password):
        login_user(user, remember=True)
        db.session.add(user)
        db.session.commit()
        return render_template('main.html', first_name= user.first_name, last_name= user.last_name)
    else:
        print("error, net usera")
        return render_template("auth.html", message="Ошибка авторизации")