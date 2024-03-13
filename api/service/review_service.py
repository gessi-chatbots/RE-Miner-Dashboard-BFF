from api import db
from api.models import User, Review, user_reviews_application_association
from sqlalchemy import insert, select, delete
import api.service.user_service as user_service
import api.service.application_service as application_service
import api.exceptions as api_exceptions
import requests
import nltk
import uuid

def validate_user_and_application(user_entity, application_entity):
    if not user_entity:
        raise api_exceptions.UserNotFoundException
    elif not application_entity:
        raise api_exceptions.ApplicationNotFoundException
    

def add_to_db_session(new_review_entity, user_entity, application_entity):
    db.session.add_all([user_entity, application_entity, new_review_entity])

def save_review(user_id, application_id, review_data):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    
    mapped_review_data = {
        "id": str(uuid.uuid4()),
        "review_id": review_data.get('reviewId', '')
    }

    new_review_entity = Review(**mapped_review_data)
    user_entity.reviews.append(new_review_entity)
    application_entity.reviews.append(new_review_entity)
    
    db.session.add_all([user_entity, application_entity, new_review_entity])
    db.session.commit()
    user_application_review_association = user_reviews_application_association.insert().values(
        user_id=user_entity.id,
        review_id=new_review_entity.id,
        application_id=application_entity.id
    )
    db.session.execute(user_application_review_association)  
    db.session.commit()
    return new_review_entity.json()

def validate_reviews(user_id, reviews):
    user = user_service.get_user_by_id(user_id)
    user_review_ids = {review.id for review in user.reviews} 
    for review in reviews:
        if review["reviewId"] not in user_review_ids:
            raise api_exceptions.ReviewNotFromUserException(review["reviewId"])

# TODO make kr service
def get_reviews_from_knowledge_repository():
    requests.get('http://127.0.0.1:3001/graph-db-api/reviews')
    return None

def is_review_splitted(review):
    return False

def split_review(review):
    sentences = nltk.sent_tokenize(review)


def analyze_reviews(user_id, reviewsIds):
    validate_reviews(user_id, reviewsIds)
    kr_reviews = get_reviews_from_knowledge_repository(reviewsIds)
    for kr_review in kr_review:
        if not is_review_splitted(kr_review):
            split_review(kr_review)
        

def analyze_review(review, feature_model, sentiment_model):
    sentences = nltk.sent_tokenize(review)
    for sentence in sentences:
        analyze_sentence_review(sentence, feature_model, sentiment_model)

def analyze_sentence_review(sentence, feature_model, sentiment_model):
    if sentiment_model != "" and feature_model != "":
        endpoint_url = requests.post(f'http://127.0.0.1:3000/analyze-reviews?model_emotion={sentiment_model}&model_features={feature_model}')
    elif sentiment_model != "" and feature_model == "":
        endpoint_url = f"http://127.0.0.1:3000/analyze-reviews?model_emotion={sentiment_model}"
    elif feature_model != None and sentiment_model == "":
        endpoint_url = f"http://127.0.0.1:3000/analyze-reviews?model_features={feature_model}"


def save_review_in_sql_db(user_id, application_id, review_data):
    if not has_user_review(user_id, application_id, review_data.get('reviewId', '')):
        return save_review(user_id, application_id, review_data)
    else:
        return api_exceptions.ReviewNotFromUserException

def delete_review(user_id, application_id, review_id):
    try:
        review = get_review_by_id(review_id)
        if not review:
            raise api_exceptions.ReviewNotFoundException
        db.session.execute(
            delete(user_reviews_application_association).where(
                (user_reviews_application_association.c.user_id == user_id) &
                (user_reviews_application_association.c.application_id == application_id) &
                (user_reviews_application_association.c.review_id == review_id)
            )
        )
        db.session.delete(get_review_by_id(review_id))
        db.session.commit()   
    except Exception as e:
        db.session.rollback()


def select_review(user_id, application_id, review_id): 
    query = select().where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id) &
        (user_reviews_application_association.c.review_id == review_id)
        
    )
    result = db.session.execute(query).fetchone()
    return result


def save_review_in_graph_db(review):
    # We should add NLTK and split the reviews
    # Expand the GraphDB
    return None

def create_review(user_id, application_id, review_data):
    review = save_review_in_sql_db(user_id, application_id, review_data)
    # save_review_in_graph_db(review)
    return review

def analyze_review(user_id, application_id, review_id, feature_model, sentiment_model):
    review = get_review(user_id, application_id, review_id)
    analyze_review(review. feature_model, sentiment_model)

    # save_review_in_graph_db(review)
    return review

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    return review

            
def process_application_reviews(user_id, application_name, reviews_data):
    for review in reviews_data:
        create_review(user_id, application_name, review)

def get_user_application_review_from_sql(user_id, application_id, review_id): 
    query = select(user_reviews_application_association).where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id) &
        (user_reviews_application_association.c.review_id == review_id)
    )
    result = db.session.execute(query).fetchone()
    if result is None:
        raise api_exceptions.ReviewNotFromUserException
    return result

def get_review_from_knowledge_repository(review_id): 
    response = requests.get(f'http://127.0.0.1:3001/graph-db-api/reviews/{review_id}')
    if response.status_code == 200:
        return response.json()
    
def select_review(user_id, application_id, review_id): 
    get_user_application_review_from_sql(user_id, application_id, review_id)
    review = get_review_from_knowledge_repository(review_id)
    return review

def get_review(user_id, application_id, review_id):
    result = select_review(user_id, application_id, review_id)
    if result:
        review_data = {"review": 
                        {"id": result[1]}
                    }
        return review_data
    else:
        raise api_exceptions.ReviewNotFoundException

def get_reviews_by_user_application(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    query = select(user_reviews_application_association.c.review_id).where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id)
    )
    results = db.session.execute(query).fetchall()
    reviews_data = {"reviews": [{'reviewId': result[0]} for result in results]}
    return reviews_data

def has_user_review(user_id, application_id, review_id):
    query = user_reviews_application_association.select().where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id) &
        (user_reviews_application_association.c.review_id == review_id)
    )
    result = db.session.execute(query).fetchone()
    return result is not None



        