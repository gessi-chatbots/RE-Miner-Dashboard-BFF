from app import db
from flask_login import UserMixin

application_review_association = db.Table(
    'application_reviews',
    db.Column('application_name', db.String, db.ForeignKey('applications.name'), primary_key=True),
    db.Column('review_id', db.String, db.ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True)
)

class Application(db.Model):
    __tablename__ = 'applications'
    name = db.Column(db.String(150), primary_key=True, unique=True)
    reviews = db.relationship(
        'Review', 
        secondary=application_review_association,
        backref=db.backref('applications', lazy='dynamic'),
        lazy='dynamic')
    
    def json(self):
        return {'name': self.name}
      
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.String(36), primary_key=True, unique=True)

    def json(self):
        return {'id': self.id}

user_application_association = db.Table(
    'user_applications',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('application_name', db.String, db.ForeignKey('applications.name'), primary_key=True)
)

user_review_association = db.Table(
    'user_reviews',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('review_id', db.String, db.ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    applications = db.relationship(
        'Application',
        secondary=user_application_association,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'    
    )
    reviews = db.relationship(
        'Review',
        secondary=user_review_association,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'family_name': self.family_name,
            'email': self.email
        }
    

