from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

# Initialize SQLAlchemy extension instance
db = SQLAlchemy()


class TierType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class GradeLevel(str, Enum):
    NINTH = "9th"
    TENTH = "10th"
    TWELFTH = "12th"


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    gmail = db.Column(db.String(120), nullable=True)
    class_val = db.Column(db.String(50), nullable=True)
    board = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    avatar_path = db.Column(db.String(255), nullable=True)


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Enum(GradeLevel, native_enum=False), nullable=False)

    # Relationship
    resources = db.relationship('Resource', backref='subject', lazy=True, cascade="all, delete-orphan")


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    tier = db.Column(db.Enum(TierType, native_enum=False), default=TierType.FREE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)