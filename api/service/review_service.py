from api import db
from api.models import User, Review, user_reviews_application_association
from sqlalchemy import insert, select, delete
from typing import List
import api.service.user_service as user_service
import api.service.application_service as application_service
import api.exceptions as api_exceptions
import requests
import nltk
import uuid
import json

class FeatureDTO:
    def __init__(self, id: str, feature: str):
        self.id = id
        self.feature = feature

    def to_dict(self):
        return {
            "id": self.id,
            "feature": self.feature,
        }

class SentimentDTO:
    def __init__(self, id: str, sentiment: str):
        self.id = id
        self.sentiment = sentiment

    def to_dict(self):
        return {
            "id": self.id,
            "sentiment": self.sentiment,
        }

class SentenceDTO:
    def __init__(self, id: str, sentiment: SentimentDTO, feature: FeatureDTO, text: str = None):
        self.id = id
        self.sentiment = sentiment
        self.feature = feature
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "sentiment data": self.sentiment,
            "feature data": self.feature,
            "text": self.text
        }

class ReviewResponseDTO:
    def __init__(self, id: str, applicationId:str, review: str, sentences: List[SentenceDTO]):
        self.reviewId = id
        self.applicationId = applicationId
        self.review = review
        self.sentences = sentences

    def to_dict(self):
        return {
            "reviewId": self.reviewId,
            "applicationId": self.applicationId,
            "review": self.review,
            "sentences": [sentence.to_dict() for sentence in self.sentences]
        }

def validate_user_and_application(user_entity, application_entity):
    if not user_entity:
        raise api_exceptions.UserNotFoundException
    elif not application_entity:
        raise api_exceptions.ApplicationNotFoundException
    

def add_to_db_session(new_review_entity, user_entity, application_entity):
    db.session.add_all([user_entity, application_entity, new_review_entity])

def save_review(user_id, application_id, review_id):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    
    mapped_review_data = {
        "id": str(uuid.uuid4()),
        "review_id": review_id
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

def validate_reviews(user_id, id_dicts):
    user = user_service.get_user_by_id(user_id)
    review_ids = [id_dict['reviewId'] for id_dict in id_dicts]
    reviews = get_reviews_by_review_id(review_ids)
    user_review_ids = {review.id for review in user.reviews} 
    for review in reviews:
        if review.id not in user_review_ids:
            raise api_exceptions.ReviewNotFromUserException(review["reviewId"])

# TODO make a kr service
def get_reviews_from_knowledge_repository(reviews):
    try:
        reviews_json = []
        if not isinstance(reviews, list):
            reviews_json.append(reviews)
        else:
            reviews_json = reviews
        response = requests.get('http://127.0.0.1:3001/graph-db-api/reviews', json=reviews_json)
        if response.status_code == 200:
            review_response_dtos = []
            for review_json in response.json():
                review_response_dtos.append(extract_review_dto_from_json(review_json))
            return review_response_dtos
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException()
    
def extract_review_dto_from_json(review_json):
    app_identifier = review_json.get('applicationId')
    id = review_json.get('reviewId')
    body = review_json.get('review')
    sentences_json = review_json.get('sentences')
    if sentences_json is not None:
        sentences = [SentenceDTO(**sentence) for sentence in sentences_json]
    else:
        sentences = []
    review_response_dto = ReviewResponseDTO(id=id, applicationId=app_identifier, review=body, sentences=sentences)
    return review_response_dto

def is_review_splitted(review):
    return review.sentences is not None and len(review.sentences) > 0

def check_review_splitting(review):
    if not is_review_splitted(review):
        extend_and_split_review(review)  
    else:
        add_sentences_to_review(review)

def extend_and_split_review(review):
    sentences = split_review(review.review)
    for index, sentence in enumerate(sentences):
        sentence_id = f"{review.reviewId}_{index}"
        feature = None
        sentiment = None
        text = sentence
        review.sentences.append(SentenceDTO(id=sentence_id, feature=feature, sentiment=sentiment, text=text))

def split_review(review_text):
    return nltk.sent_tokenize(review_text)

def add_sentences_to_review(review):
    sentences = split_review(review.review)
    for index, sentence in enumerate(sentences):
        review.sentences[index].text = sentence

def send_to_hub_for_analysis(reviews, feature_model, sentiment_model):
    endpoint_url = ""
    if (sentiment_model is not None and sentiment_model != "") and (feature_model is not None and feature_model != ""):
        endpoint_url = f'http://127.0.0.1:3000/analyze?sentiment_model={sentiment_model}&feature_model={feature_model}'
    elif (sentiment_model is not None and sentiment_model != "") and (feature_model is None or feature_model == ""):
        endpoint_url = f"http://127.0.0.1:3000/analyze?sentiment_model={sentiment_model}"
    elif (feature_model is not None and feature_model != "") and (sentiment_model is None or sentiment_model == ""):
        endpoint_url = f"http://127.0.0.1:3000/analyze?feature_model={feature_model}"
    reviews_dict = [review.to_dict() for review in reviews]
    response = requests.post(endpoint_url, json=json.dumps(reviews_dict))
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise api_exceptions.HUBException()
    
def analyze_reviews(user_id, reviewsIds, feature_model, sentiment_model):
    validate_reviews(user_id, reviewsIds)
    kr_reviews = get_reviews_from_knowledge_repository(reviewsIds)
    for kr_review in kr_reviews:
        check_review_splitting(kr_review)
    analyzed_reviews = send_to_hub_for_analysis(kr_reviews, feature_model, sentiment_model)
    send_reviews_to_kg(analyzed_reviews)



def send_reviews_to_kg(reviews):
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            'http://127.0.0.1:3001/graph-db-api/reviews',
            headers=headers,
            json=(reviews if isinstance(reviews, list) else [reviews])
        )
        if response.status_code == 201:
            return response.json
        else:
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException()


def save_review_in_sql_db(user_id, application_id, review_id):
    if not has_user_review(user_id, application_id, review_id):
        return save_review(user_id, application_id, review_id)
    else:
        return api_exceptions.ReviewNotFromUserException

def delete_review(user_id, application_id, review_id):
    try:
        review = get_review_by_review_id(review_id)
        get_user_application_review_from_sql(user_id, application_id, review.id)
        db.session.execute(
            delete(user_reviews_application_association).where(
                (user_reviews_application_association.c.user_id == user_id) &
                (user_reviews_application_association.c.application_id == application_id) &
                (user_reviews_application_association.c.review_id == review_id)
            )
        )
        db.session.delete(review)
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

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    return review


def get_review_by_review_id(review_id):
    review = Review.query.filter_by(review_id=review_id).one_or_none()
    if review is None:
        raise api_exceptions.ReviewNotFoundException(review_id)
    return review

def get_reviews_by_review_id(review_ids):
    reviews = Review.query.filter(Review.review_id.in_(review_ids)).all()
    return reviews
            
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
        raise api_exceptions.ReviewNotFromUserException(review_id, user_id)
    return result

def get_review(user_id, application_id, review_id):
    review = get_review_by_review_id(review_id)
    get_user_application_review_from_sql(user_id, application_id, review.id)
    reviews = get_reviews_from_knowledge_repository({"reviewId": review_id})
    review = reviews[0]
    return review

def get_reviews_by_user_application(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    query = select(user_reviews_application_association.c.review_id).where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id)
    )
    results = db.session.execute(query).fetchall()
    user_reviews = [result[0] for result in results]
    reviews_ids = []
    for user_review_id in user_reviews:
        review = get_review_by_id(user_review_id)
        reviews_ids.append(review.json())
    return reviews_ids

def has_user_review(user_id, application_id, review_id):
    query = user_reviews_application_association.select().where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id) &
        (user_reviews_application_association.c.review_id == review_id)
    )
    result = db.session.execute(query).fetchone()
    return result is not None



        