from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Tier Types for Resources
class TierType(Enum):
    FREE = "free"
    PREMIUM = "premium"

# Grade/Class Categories
class GradeLevel(Enum):
    NINTH = "9th"
    TENTH = "10th"
    TWELFTH = "12th"

# --------------------------------------------------------------------------
# User Model
# --------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    purchases = db.relationship('Purchase', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

# --------------------------------------------------------------------------
# Subject Model
# --------------------------------------------------------------------------
class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Enum(GradeLevel), nullable=False)  # '9th', '10th', '12th'
    description = db.Column(db.Text, nullable=True)

    # Relationships
    resources = db.relationship('Resource', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name} - Class {self.grade.value}>'

# --------------------------------------------------------------------------
# Academic Resource Model (PDF Vault / Notes / PYQs)
# --------------------------------------------------------------------------
class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)  # Storage path/URL for PDF or material
    tier = db.Column(db.Enum(TierType), default=TierType.FREE, nullable=False)
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Resource {self.title} [{self.tier.value}]>'

# --------------------------------------------------------------------------
# Purchase / Subscription Model
# --------------------------------------------------------------------------
class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Purchase Txn:{self.transaction_id} User:{self.user_id}>'