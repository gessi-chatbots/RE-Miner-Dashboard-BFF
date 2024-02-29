from app import db
from app.models import Review
from flask import jsonify
import app.users_api.service as users_api_service
import app.applications_api.service as applications_api_service
from sqlalchemy.exc import IntegrityError


def add_to_db_session(new_review_entity, user_entity, application_entity):
    db.session.add_all([user_entity, application_entity, new_review_entity])

def create_review(user_id, application_name, review_data, commit=False):
    user_entity = users_api_service.get_user_by_id(user_id)
    application_entity = applications_api_service.get_application_by_name(application_name)
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

                
def save_review_in_sql_db(user_id, application_entity, review_data, commit = False):
    review_entity = get_review_by_id(review_data.get('reviewId', ''))
    if review_entity is None:
        return create_review(user_id, application_entity, review_data, commit)
    else:
        return review_entity.json()    

# TODO
def save_review_in_graph_db(review):
    # We should add NLTK and split the reviews
    # Expand the GraphDB
    return None

def process_review(user_id, application_name, review_data, commit = False):
    save_review_in_sql_db(user_id, application_name, review_data, commit)
    # save_review_in_graph_db(review)

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    return review

def get_review_data(id):
    review = get_review_by_id(id)
    review_data = {
        "reviewId": review.id
    }
    return review_data

def process_application_reviews(user_id, application_name, reviews_data):
    for review in reviews_data:
        process_review(user_id, application_name, review, commit=False)

def get_all_reviews_from_user(user_id):
    user = users_api_service.get_user_by_id(user_id)
    reviews = user.reviews.all()
    review_list = {
        "reviews" : [{'reviewId': review.id} for review in reviews]     
    }
    return review_list

def is_review_from_user(review_id, user_id):
    user_entity = users_api_service.get_user_by_id(user_id)
    if user_entity.reviews:
        return review_id in [review.id for review in user_entity.reviews]
    else: 
        return False
