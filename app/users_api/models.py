from app import db

user_application_association = db.Table('user_applications',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('application_name', db.String, db.ForeignKey('applications.name'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    applications = db.relationship(
        'Application', secondary=user_application_association,
        backref=db.backref('users', lazy='dynamic'))
    
    def json(self):
        return {'id': self.id,
                'name': self.name, 
                'family_name': self.family_name,
                'email': self.email}

