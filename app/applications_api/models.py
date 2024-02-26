from app import db

application_review_association = db.Table(
    'application_reviews',
    db.Column('application_name', db.String, db.ForeignKey('applications.name'), primary_key=True),
    db.Column('review_id', db.String, db.ForeignKey('reviews.id'), primary_key=True)
)


class Application(db.Model):
    __tablename__ = 'applications'
    name = db.Column(db.String(150), primary_key=True, unique=True)
    reviews = db.relationship(
        'Review', secondary=application_review_association,
        backref=db.backref('reviews', lazy='dynamic'))
    
    def json(self):
        return {'name': self.name}

