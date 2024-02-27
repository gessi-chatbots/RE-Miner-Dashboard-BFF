from . import ReviewNotFound
from .models import Review, db
from sqlalchemy.exc import IntegrityError

def save_review_in_sql_db(application_name, review):
    try:
        db.session.begin_nested()
        review_data = {
            'id': review.get('reviewId')
        }
        new_review = Review(**review_data)
        db.session.add(new_review)
        db.session.commit()
        return new_review.json()
    except IntegrityError as e:
        print('Review already exists rollbacking...')
        db.session.rollback()

# TODO
def save_review_in_graph_db(review):
    # We should add NLTK and split the reviews
    # Expand the GraphDB
    return None

def process_review(application_name, review):
    save_review_in_sql_db(application_name, review)
    save_review_in_graph_db(review)

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    if review is None: 
        raise ReviewNotFound()
    return review

def process_application_reviews(application_name, reviews):
    for review in reviews:
        process_review(application_name, review)