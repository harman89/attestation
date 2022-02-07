import datetime
from unicodedata import name

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import *

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'df9d9b8a053375dbae2758d00192748b77c1208ddd6e478c65b35e982c3c633b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    #персональные данные
    id = Column(Integer(), primary_key=True)
    login = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    mid_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    #id грейда
    current_grade_id = Column(Integer,ForeignKey('grade.id'))
    #id позиции
    position_id=Column(Integer, ForeignKey('position.id'))
    #остальные персональные данные
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    admin_flg = Column(Boolean, nullable=False)
    active_flg = Column(Boolean, nullable=False)
    can_approve_flg = Column(Boolean, nullable=False)
    picture_path = Column(String(255))
    city = Column(String(255))
    #next_certification_dt = Column(DateTime)
    #связь с intersection таблицей хранящей инфу о скиллах конкретного работника 
    user_skill = relationship('User_Skill',backref='user', lazy = 'dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"user {self.username}"

class Skill(db.Model):
    __tablename__ ="skill"
    #персональные данные
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))

    #у навыков есть категории, уровень вложенности которых может быть разным. Поэтому решили хранить в записе о навыке
    #ссылку на корневой элемент(самая верхняя категория) и родительский элемент
    #при помощи этого можно нормально выводить список навыков с категориями

    #корневой элемент дерева навыков
    root_id = Column(Integer(), nullable=False)
    #родительский элемент дерева навыков
    parent_id = Column(Integer())

    #личная инфа
    active_flg = Column(Boolean, nullable=False)
    link_to_lesson = Column(String(255))
    #уровень вложенности
    level = Column(Integer(), nullable=False) 
    #связь с таблицей навыков
    user_skill = relationship('User_Skill',backref='user_skill', lazy = 'dynamic')
    #связь с таблицей грейдов
    grade_skill = relationship('Grade_Skill',backref='grade_skill', lazy = 'dynamic')

class Grade(db.Model):
    __tablename__ ="grade"
    #личные данные
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    #хз
    position = Column(Integer(), nullable=False)
    #зачем это нужно?
    #level_id = Column(Integer(), nullable=False)

    #связь с таблицей навыков. у грейда есть навыки с минимальным уровнем владения
    grade_skill = relationship('Grade_Skill',backref='grade', lazy = 'dynamic')
    #грейд хранит ид позиции. Зачем не помню, лол
    position_id = Column(Integer(), ForeignKey('position.id'))

class Position(db.Model):
    __tablename__ ="position"
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)

    #позицию используем в таблице пользователь и грейд.
    user_position = relationship('User',backref='user_position',lazy = 'dynamic')
    grade_position = relationship('Grade',backref='grade_position', lazy = 'dynamic')

class User_Skill(db.Model):
    __tablename__ ="user_skill"
    id = Column(Integer(), primary_key=True)
    #какой юзер
    user_id = Column(Integer(), ForeignKey('user.id'))
    #какой навык
    skill_id = Column(Integer(), ForeignKey('skill.id'))
    #какой уровень владения навыком
    level_id = Column(Integer(), ForeignKey('level.id'))
    #метаданные
    created= Column(Integer(), nullable=False)
    updated= Column(Integer(), nullable=False)
    #подтвержден
    approved_flg= Column(Boolean(), nullable=False)
    #кто подтвердил
    approver_id= Column(Integer(), nullable=False)

class Level(db.Model):
    __tablename__ = "level"
    id = Column(Integer(), primary_key=True)
    #зачем код
    letter_code = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    #неясно зачем грейду нужен уровень, мб имелось ввиду что то другое
    #grade=relationship('Grade',backref='level', lazy = 'dynamic')
    #grade_skill хранит минимальный уровень владения для грейда
    grade_skill = relationship('Grade_Skill', backref='grade_skill_level', lazy = 'dynamic')
    #у навыка, которым владеет сотрудник определённый уровень
    user_skill = relationship('User_Skill', backref='user_skill_level', lazy = 'dynamic')

class Grade_Skill(db.Model):
    __tablename__ ="grade_skill"
    id = Column(Integer(), primary_key=True)
    #связываем навык с грейдом, выставляем минимальный уровень
    grade_id = Column(Integer(), ForeignKey('grade.id'))
    skill_id = Column(Integer(), ForeignKey('skill.id'))
    min_level_id = Column(Integer(), ForeignKey('level.id'))
