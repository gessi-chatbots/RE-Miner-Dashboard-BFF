from api import db
from api.models import User, Review
import api.service.user_service as user_service
import api.service.application_service as application_service

def add_to_db_session(new_review_entity, user_entity, application_entity):
    db.session.add_all([user_entity, application_entity, new_review_entity])

def save_review(user_id, application_id, review_data):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    if not user_entity or not application_entity:
        return None
    mapped_review_data = {
        "id": review_data['reviewId']
    }
    new_review_entity = Review(**mapped_review_data)
    user_entity.reviews.append(new_review_entity)
    application_entity.reviews.append(new_review_entity)
    add_to_db_session(new_review_entity, application_entity, user_entity)
    db.session.commit()
    return new_review_entity.json()

                
def save_review_in_sql_db(user_id, application_id, review_data):
    review_entity = get_review_by_id(review_data.get('reviewId', ''))
    if review_entity is None:
        return save_review(user_id, application_id, review_data)
    else:
        return review_entity.json()    

def delete_review(review_id):
    review = get_review_by_id(review_id)
    try:
        db.session.delete(review)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
# TODO
def save_review_in_graph_db(review):
    # We should add NLTK and split the reviews
    # Expand the GraphDB
    return None

def create_review(user_id, application_id, review_data):
    review = save_review_in_sql_db(user_id, application_id, review_data)
    # save_review_in_graph_db(review)
    return review

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    return review

def get_review(user_id, application_id, review_id):
    user = User.query.get(user_id)
    # TODO handle exceptions
    if user:
        application = user.applications.filter_by(id=application_id).first()
        if application:
            review = user.applications.reviews.filter_by(id=review_id).first()
            if review:
                review_data = {
                    "id": review.id
                }
                return review_data
            
def process_application_reviews(user_id, application_name, reviews_data):
    for review in reviews_data:
        create_review(user_id, application_name, review)

def get_reviews(user_id):
    user = user_service.get_user_by_id(user_id)
    reviews = user.reviews.all()
    review_list = {
        "reviews" : [{'reviewId': review.id} for review in reviews]     
    }
    return review_list

def is_review_from_user(user_id, application_id, review_id):
    user = User.query.get(user_id)
    # TODO handle exceptions
    if user:
        application = user.applications.filter_by(id=application_id).first()
        if application:
            review = user.applications.reviews.filter_by(id=review_id).first()
            return review is not None

