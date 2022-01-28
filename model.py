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
    id = Column(Integer(), primary_key=True)
    login = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    mid_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    current_grade_id = Column(Integer,ForeignKey('grade.id'))
    position_id=Column(Integer, ForeignKey('position.id'))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    admin_flg = Column(Boolean, nullable=False)
    active_flg = Column(Boolean, nullable=False)
    can_approve_flg = Column(Boolean, nullable=False)
    picture_path = Column(String(255))
    city = Column(String(255))
   #next_certification_dt = Column(DateTime)
    user_skill = relationship('User_Skill',backref='user', lazy = 'dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"user {self.username}"

class Skill(db.Model):
    __tablename__ ="skill"
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    root_id = Column(Integer(), nullable=False)
    parent_id = Column(Integer())
    active_flg = Column(Boolean, nullable=False)
    link_to_lesson = Column(String(255))
    level = Column(Integer(), nullable=False) #уровень вложенности
    user_skill = relationship('User_Skill',backref='skill', lazy = 'dynamic')
    grade_skill = relationship('Grade_Skill',backref='skill', lazy = 'dynamic')

class Grade(db.Model):
    __tablename__ ="grade"
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    position = Column(Integer(), nullable=False)
    
    level_id = Column(Integer(), nullable=False)#зачем это нужно?

    grade_skill = relationship('Grade_Skill',backref='grade', lazy = 'dynamic')
    position_id = Column(Integer(), ForeignKey('position.id'))

class Position(db.Model):
    __tablename__ ="position"
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    user_position = relationship('User',backref='position',lazy = 'dynamic')
    grade_position = relationship('Grade',backref='position', lazy = 'dynamic')

class User_Skill(db.Model):
    __tablename__ ="user_skill"
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('user.id'))
    skill_id = Column(Integer(), ForeignKey('skill.id'))
    level_id = Column(Integer(), ForeignKey('level.id'))
    created= Column(Integer(), nullable=False)
    updated= Column(Integer(), nullable=False)
    approved_flg= Column(Boolean(), nullable=False)
    approver_id= Column(Integer(), nullable=False)

class Level(db.Model):
    __tablename__ = "level"
    id = Column(Integer(), primary_key=True)
    letter_code = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    grade=relationship('grade',backref='level', lazy = 'dynamic')
    grade_skill = relationship('Grade_Skill', backref='level', lazy = 'dynamic')
    user_skill = relationship('User_Skill', backref='level', lazy = 'dynamic')

class Grade_Skill(db.Model):
    __tablename__ ="grade_skill"
    id = Column(Integer(), primary_key=True)
    grade_id = Column(Integer(), ForeignKey('grade.id'))
    skill_id = Column(Integer(), ForeignKey('skill.id'))
    min_level_id = Column(Integer(), ForeignKey('level.id'))
