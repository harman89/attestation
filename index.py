import datetime
import random
import string
import xml.etree.ElementTree as ET
from os.path import dirname, join, realpath,exists

import flask
from flask import render_template, request, jsonify, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from model import db, Lecture, app, User, Test, Question, Course, Answer, Group, InviteCode,GroupCourse,UserGroup,Marks,Part,Notification

db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = '/'

def insert_admin():
    if not db.session.query(User).filter(User.username == "admin").first():
        user = User(username="admin", name="admin", surname="admin", email="admin@admin.ru", role="admin")
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()

insert_admin()

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route("/add_course", methods=['POST'])
@login_required
def add_course():
    if not db.session.query(Course).filter(Course.title == request.form.get("title")).first():
        title = request.form.get('title')
        course = Course(title=title)
        db.session.add(course)
        db.session.commit()
        return show_course_panel()
    else:
        return show_course_panel(message="Курс с таким именем уже существует !!!")


@app.route("/add_group_to_course", methods=['POST'])
@login_required
def add_groupcourse():
    course_id = request.form.get('course_id')
    if not db.session.query(GroupCourse).filter(GroupCourse.course_id==request.form.get('course_id')).filter(GroupCourse.group_id==request.form.get('group_id')).first():
        group_id = request.form.get('group_id')
        groupcourse = GroupCourse(group_id=group_id, course_id = course_id)
        db.session.add(groupcourse)
        db.session.commit()
        return show_course_overview(course_id,message="Группа успешно прикреплена к курсу")
    else:
        return show_course_overview(message="Эта группа уже прикреплена к курсу", course_id=course_id)


@app.route('/test<test_id>', methods=['GET', 'POST'])
@login_required
def show_test(test_id):
    course_id = request.form.get("course_id")
    if course_id is None:
        course_id = request.args.get("course_id")
    print(test_id)
    print(course_id)
    test = db.session.query(Test).filter(Test.id == test_id).first()
    parts = db.session.query(Part).filter(Part.test_id == test_id).all()
    return render_template("test.html", title=test.title, test_id =test_id, course_id=course_id, parts=parts)



@app.route('/part<part_id>', methods=['POST'])
@login_required
def show_part(part_id, message=""):
    course_id = request.form.get("course_id")
    test_id = request.form.get("test_id")
    if not part_id:
        part_id = request.form.get("part_id")
    print(test_id)
    print(course_id)
    print(part_id, "part")
    part = db.session.query(Part).filter(Part.id == part_id).first()
    print(part)
    if test_id is None:
        test_id=part.test_id
    if course_id is None:
        test = db.session.query(Test).filter(Test.id ==test_id).first()
        course_id = test.course_id
    count = 0
    for _ in part.question.all():
        count += 1
    return render_template("part.html", title=part.text, questions=part.question.all(), count=count,test_id =test_id, course_id=course_id, part_id = part_id)


@app.route('/lecture<lecture_id>', methods=['POST'])
@login_required
def show_lecture(lecture_id):
    course_id = request.form.get("course_id")
    lecture = db.session.query(Lecture).filter(Lecture.id == lecture_id).first()
    return render_template("lecture.html", lecture=lecture, course_id=course_id)


@app.route('/add_test', methods=['POST'])
def add_test():
    course_id = request.form.get("course_id")
    if not db.session.query(Test).filter(Test.title == request.form.get("title")).first():
        course = db.session.query(Course).filter(Course.id == course_id).first()
        test = Test(title=request.form.get("title"), course=course)
        test.close_date = datetime.datetime.strptime(request.form.get("close_date"), "%Y-%m-%d").date()
        db.session.add(test)
        db.session.commit()
        return show_course_control_panel(message="Тест успешно добавлен", course_id=course_id)
    else:
        return show_course_control_panel(message="Тест с таким именем уже существует !!!", course_id=course_id)


@app.route('/add_part', methods=['POST'])
def add_part():
    test_id = request.form.get("test_id")
    course_id = request.form.get("course_id")
    if not db.session.query(Part).filter(Part.text == request.form.get("title")).first():
        test = db.session.query(Test).filter(Test.id == test_id).first()
        number = db.session.query(Part).filter(Part.test_id==test_id).count()
        number=number+1
        part = Part(text=request.form.get("title"), test=test)
        part.number=number
        db.session.add(part)
        db.session.commit()
        return show_course_control_panel(message="Раздел теста успешно добавлен", course_id=course_id)
    else:
        return show_course_control_panel(message="Раздел теста с таким именем уже существует !!!", course_id=course_id)


@app.route('/add_question_in_part', methods=['POST'])
def add_question_in_part():
    part_id = request.form.get("part_id")
    print(part_id)
    part = db.session.query(Part).filter(Part.id == part_id).first()
    if part:
        count = 0
        for _ in part.question.all():
            count += 1
        question = Question(title=request.form.get(
            "question_title"), part=part, number = count)
        db.session.add(question)
        radio = request.form.get("radio")
        for i in range(1, 7):
            if request.form.get(f"answer{i}") != "":
                if radio == f"radio{i}":
                    db.session.add(Answer(text=request.form.get(
                    f"answer{i}"),question=question,isTrue = 1))
                else:
                    db.session.add(Answer(text=request.form.get(
                    f"answer{i}"),question=question,isTrue = 0))
        db.session.commit()
        return show_part(message="Вопрос успешно добавлен", part_id = part_id)
    else:
        return show_part(message="Ошибка",part_id = part_id)


@app.route("/edit_question_submit", methods=['POST'])
@login_required
def edit_question_submit():
    question_id = request.form.get("question_id")
    question = db.session.query(Question).filter(Question.id == question_id).first()
    part_id = question.part_id
    question.title = request.form.get("question_title")
    db.session.add(question)
    radio = request.form.get("radio")
    answers = db.session.query(Answer).filter(Answer.question_id == question.id).all()
    for answer in answers:
        answer.text = request.form.get(f"answer{answer.id}")
        if radio == f"radio{answer.id}":
            answer.isTrue = 1
        else:
            answer.isTrue = 0
        db.session.add(question)
    db.session.commit()
    return show_part(message="Вопрос успешно добавлен", part_id = part_id)


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
    db.session.add(InviteCode(text=code))
    db.session.commit()
    return show_admin_panel(message=f"Код приглашения  - {code}")


@app.route("/generate_new_group", methods=['POST'])
@login_required
def generate_new_group():
    choice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in [i for i in list(string.ascii_lowercase + string.ascii_uppercase)]:
        choice.append(i)
    code = ""
    for i in range(6):
        code += str(random.choice(choice))
    question = Group(name=request.form.get("group_name"), code=code)
    db.session.add(question)
    db.session.commit()
    usergroup = UserGroup(group_id = question.id, user_id = current_user.id)
    print(usergroup.id,usergroup.group_id,usergroup.user_id)
    db.session.add(usergroup)
    db.session.commit()
    return show_groups_panel(message=f"Сгенерированный код - {code}")


@app.route('/')
def index(message=""):
    if current_user.is_authenticated:
        return show_course_panel()
    else:
        return render_template('login.html', message=message)


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
            return render_template('login.html', message="Успешная регистрация")
        else:
            return render_template('login.html', message="Неверный код приглашения")
    else:
        return render_template('registration.html')


@app.route('/registration_student', methods=['GET', 'POST'])
def registration_student():
    print(request.get_json())
    if flask.request.method == 'POST':
        request_for_registration = request.get_json()
        print(request_for_registration)
        group = db.session.query(Group).filter(Group.code==request_for_registration['code']).first()
        if group is not None:
            user = User(username=request_for_registration['username'], surname=request_for_registration['surname'],
                        name=request_for_registration['name'],
                        email=request_for_registration['mail'], role = "student")
            user.set_password(request_for_registration['password'])
            db.session.add(user)
            db.session.commit()
            usergroup = UserGroup(group_id=group.id, user_id=user.id)
            db.session.add(usergroup)
            db.session.commit()
            return jsonify({'message':'Registration completed'})
        else:
            return jsonify({'message':'invalid group code'})
    else:
        return jsonify({'message':'not post'})


@app.route('/exit')
@login_required
def logout():
    logout_user()
    return render_template('login.html')


@app.route("/admin")
def show_admin_panel(message=""):
    if current_user.is_authenticated:
        if current_user.role == "admin":
            users = db.session.query(User).all()
            return render_template("admin.html", users_list=users, message=message)
        else:
            return index(message="Отказано в доступе")
    else:
        return index(message="Отказано в доступе")


@app.route("/course_panel")
@login_required
def show_course_panel(message=""):
    course_list = db.session.query(Course).all()
    return render_template("course_panel.html", course_list=course_list, message=message)


@app.route("/notifications")
@login_required
def show_notifications(message=""):
    groups = db.session.query(UserGroup).filter(UserGroup.user_id==current_user.id).all()
    groups_list=[]
    if groups:
        for i in groups:
            group = db.session.query(Group).filter(Group.id == i.group_id).first()
            groups_list.append(group)
    notifications=[]
    if groups_list:
        for i in groups_list:
            notifications.append(db.session.query(Notification).filter(Notification.group_id==i.id).all())
    return render_template("notifications.html", message=message,zip=zip,notifications = notifications,groups_list=groups_list)


@app.route("/send_notification", methods=['POST'])
@login_required
def send_notification(message=""):
    text = request.form.get("notification_text")
    group_id = request.form.get("group_id")
    notification = Notification(text =text, date = datetime.datetime.now(), group_id=group_id)
    db.session.add(notification)
    db.session.commit()
    groups = db.session.query(UserGroup).filter(UserGroup.user_id==current_user.id).all()
    groups_list=[]
    if groups:
        for i in groups:
            group = db.session.query(Group).filter(Group.id == i.group_id).first()
            groups_list.append(group)
    notifications=[]
    if groups_list:
        for i in groups_list:
            notifications.append(db.session.query(Notification).filter(Notification.group_id==i.id).all())
    return render_template("notifications.html", message=message,zip=zip,notifications = notifications,groups_list=groups_list)

@app.route("/groups_panel")
@login_required
def show_groups_panel(message=""):
    groups = db.session.query(UserGroup).filter(UserGroup.user_id==current_user.id).all()
    groups_list=[]
    if groups:
        for i in groups:
            group = db.session.query(Group).filter(Group.id == i.group_id).first()
            groups_list.append(group)
    return render_template("groups_panel.html", groups_list=groups_list, message=message)


@app.route("/edit_question<question_id>", methods=['POST'])
@login_required
def edit_question(question_id):
    course_id = request.form.get("course_id")
    test_id = request.form.get("test_id")
    question = db.session.query(Question).filter(Question.id == question_id).first()
    answers = db.session.query(Answer).filter(Answer.question_id == question.id).all()
    return render_template("edit_question.html", question = question, answers = answers, test_id = test_id, course_id = course_id)

@app.route("/course_control_panel<course_id>")
@login_required
def show_course_control_panel(course_id, message=""):
    tests = db.session.query(Test).filter(Test.course_id == course_id).all()
    lectures = db.session.query(Lecture).filter(Lecture.course_id == course_id).all()
    return render_template("course_control_panel.html", tests=tests, lectures=lectures, message=message,
                           course_id=course_id)


@app.route("/course<course_id>")
@login_required
def show_course_overview(course_id, message=""):
    tests = db.session.query(Test).filter(Test.course_id == course_id).all()
    lectures = db.session.query(Lecture).filter(Lecture.course_id == course_id).all()
    groups = db.session.query(UserGroup).filter(UserGroup.user_id==current_user.id).all()
    if groups:
        groups_list=[]
        for i in groups:
            group = db.session.query(Group).filter(Group.id == i.group_id).first()
            groups_list.append(group)
        return render_template("course_overview.html", tests=tests, lectures=lectures, course_id=course_id,groups = groups_list,message = message)
    else:
        return render_template("course_overview.html", tests=tests, lectures=lectures, course_id=course_id,groups = [],message = message)


@app.route("/delete_course<course_id>", methods=['POST'])
@login_required
def delete_course(course_id, message=""):
    course = db.session.query(Course).filter(Course.id == course_id).first()
    db.session.delete(course)
    db.session.commit()
    return show_course_panel()


@app.route('/educate')
def show_educate_page():
    if current_user.is_authenticated:
        return render_template('course_panel.html')
    else:
        return index(message="Отказано в доступе")


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = db.session.query(User).filter(User.username == username).first()
    if user and user.check_password(password):
        login_user(user, remember=True)
        user.last_login_time = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        return show_course_panel()
    else:
        return render_template("login.html", message="Ошибка авторизации")