from app import db


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.String(36), primary_key=True, unique=True)

    def json(self):
        return {'id': self.id}

