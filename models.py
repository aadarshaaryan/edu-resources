from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class TierType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class GradeLevel(str, Enum):
    NINTH = "9th"
    TENTH = "10th"
    TWELFTH = "12th"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    purchases = db.relationship('Purchase', backref='user', lazy=True, cascade="all, delete-orphan")

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    class_val = db.Column(db.String(50), nullable=True)
    board = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    avatar_path = db.Column(db.String(255), nullable=True)

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Enum(GradeLevel, native_enum=False), nullable=False)

    resources = db.relationship('Resource', backref='subject', lazy=True, cascade="all, delete-orphan")

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    tier = db.Column(db.Enum(TierType, native_enum=False), default=TierType.FREE, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)