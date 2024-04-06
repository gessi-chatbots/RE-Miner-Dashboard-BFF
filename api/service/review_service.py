from api import db
from api.models import User, Review, user_reviews_application_association, user_review_association
from sqlalchemy import insert, select, delete, exc, func
from typing import List
from datetime import date 
import api.service.user_service as user_service
import api.service.application_service as application_service
import api.exceptions as api_exceptions
import requests
import nltk
import uuid
import json
import os
import math


class FeatureDTO:
    def __init__(self, feature: str):
        self.feature = feature

    def to_dict(self):
        return {
            "feature": self.feature,
        }

class SentimentDTO:
    def __init__(self, sentiment: str):
        self.sentiment = sentiment

    def to_dict(self):
        return {
            "sentiment": self.sentiment,
        }

class SentenceDTO:
    def __init__(self, id: str, sentimentData: SentimentDTO, featureData: FeatureDTO, text: str = None):
        self.id = id
        self.sentimentData = sentimentData
        self.featureData = featureData
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "sentimentData": self.sentimentData.to_dict() if self.sentimentData is not None else None,
            "featureData": self.featureData.to_dict() if self.featureData is not None else None,
            "text": self.text
        }

class ReviewResponseDTO:
    def __init__(self, id: str, applicationId:str, review: str, date: date, sentences: List[SentenceDTO]):
        self.reviewId = id
        self.applicationId = applicationId
        self.review = review
        self.sentences = sentences
        self.date = date

    def to_dict(self):
        return {
            "reviewId": self.reviewId,
            "applicationId": self.applicationId,
            "review": self.review,
            "date": self.date,
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
            raise api_exceptions.ReviewNotFromUserException(review_id=review.review_id, user_id=user_id)

# TODO make a kr service
def get_reviews_from_knowledge_repository(reviews):
    try:
        reviews_json = []
        if not isinstance(reviews, list):
            reviews_json.append(reviews)
        else:
            reviews_json = reviews
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/reviews'
        response = requests.get(url, json=reviews_json)
        if response.status_code == 200:
            review_response_dtos = []
            for review_json in response.json():
                review_response_dtos.append(extract_review_dto_from_json(review_json))
            return review_response_dtos
        elif response.status_code == 404:
            raise api_exceptions.KGRReviewsNotFoundException
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException()
    
def extract_review_dto_from_json(review_json):
    app_identifier = review_json.get('applicationId')
    id = review_json.get('reviewId')
    body = review_json.get('review')
    sentences_json = review_json    .get('sentences')
    date = review_json.get('date')
    sentences = []
    if sentences_json is not None:
        for sentence_json in sentences_json:
            sentence = SentenceDTO(id=sentence_json.get('id'), sentimentData=None, featureData=None)
            if 'sentimentData' in sentence_json:
                sentimentData = sentence_json.get('sentimentData', None)
                if sentimentData is not None:
                    sentimentDTO = SentimentDTO(sentiment=sentimentData.get('sentiment'))
                    sentence.sentimentData = sentimentDTO
            if 'featureData' in sentence_json: 
                featureData = sentence_json.get('featureData', None)
                if featureData is not None:
                    featureDTO = FeatureDTO(feature=featureData.get('feature'))
                    sentence.featureData = featureDTO
            sentences.append(sentence)
    review_response_dto = ReviewResponseDTO(id=id, applicationId=app_identifier, review=body, date=date, sentences=sentences)
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
        text = sentence
        review.sentences.append(SentenceDTO(id=sentence_id, featureData=None, sentimentData=None, text=text))

def split_review(review_text):
    return nltk.sent_tokenize(review_text)

def add_sentences_to_review(review):
    sentences = split_review(review.review)
    try:
        if len(review.sentences) > 0:
            for index, sentence in enumerate(sentences):
                review.sentences[index].text = sentence
    except IndexError: # NLTK sometimes splits randomly
            sentence_id = f"{review.reviewId}_{index + 1}"
            review.sentences.append(SentenceDTO(id=sentence_id, featureData=None, sentimentData=None, text=sentence))


def send_to_hub_for_analysis(reviews, feature_model, sentiment_model):
    hub_url = 'http://127.0.0.1:3002'
    endpoint_url = hub_url + '/analyze'
    
    if sentiment_model and feature_model:
        endpoint_url += f'?sentiment_model={sentiment_model}&feature_model={feature_model}'
    elif sentiment_model:
        endpoint_url += f'?sentiment_model={sentiment_model}'
    elif feature_model:
        endpoint_url += f'?feature_model={feature_model}'

    reviews_dict = [review.to_dict() for review in reviews]
    response = requests.post(endpoint_url, json=reviews_dict)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise api_exceptions.HUBException()
    
def analyze_reviews(user_id, reviewsIds, feature_model, sentiment_model):
    # validate_reviews(user_id, reviewsIds)
    kr_reviews = get_reviews_from_knowledge_repository(reviewsIds)
    if kr_reviews is None:
        raise api_exceptions.KGRReviewsNotFoundException()
    for kr_review in kr_reviews:
        check_review_splitting(kr_review)
    analyzed_reviews = send_to_hub_for_analysis(kr_reviews, feature_model, sentiment_model)
    send_reviews_to_kg(analyzed_reviews)
    return analyzed_reviews
    



def send_reviews_to_kg(reviews):
    try:
        headers = {'Content-type': 'application/json'}
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/reviews'
        response = requests.post(
            url,
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
        review = get_review_by_review_id(user_id, application_id, review_id)
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
    except exc.IntegrityError:
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

def create_review(user_id, application_id, review_id):
    review = save_review_in_sql_db(user_id, application_id, review_id)
    # save_review_in_graph_db(review)
    return review

def get_review_by_id(id):
    review = Review.query.filter_by(id=id).one_or_none()
    return review


def get_review_by_review_id(user_id, application_id, review_id):
    reviews = Review.query.filter_by(review_id=review_id).all()
    if len(reviews) == 0 or reviews is None:
        raise api_exceptions.ReviewNotFoundException(user_id=user_id, application_id=application_id, review_id=review_id)
    user = user_service.get_user_by_id(user_id)
    application = user.applications.filter_by(id=application_id).first()
    if application is None:
        raise api_exceptions.ApplicationNotFoundException()
    if application:
        for review in reviews:
            result = db.session.execute(
                select(user_reviews_application_association).where(
                    (user_reviews_application_association.c.user_id == user_id) &
                    (user_reviews_application_association.c.application_id == application_id) &
                    (user_reviews_application_association.c.review_id == review.id)
                )
            ).fetchone()
            if result:
                return review


def get_review_from_knowledge_repository(review_id):
    return None


def get_reviews_by_review_id(review_ids):
    reviews = Review.query.filter(Review.review_id.in_(review_ids)).all()
    return reviews
            
def process_application_reviews(user_id, application_name, reviews_data):
    for review in reviews_data:
        create_review(user_id, application_name, review['reviewId']) #TODO handle exception: review does not have id

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
    review_sql = get_review_by_review_id(user_id, application_id, review_id)
    review_kr = get_reviews_from_knowledge_repository({"reviewId": review_id})[0]
    app = application_service.get_application_by_id(application_id)
    add_sentences_to_review(review_kr)
    review_data = {
        "application": {
            "id" : application_id,
            "name" : app.name.replace('_',' ')
        },
        "id":review_sql.id,
        "review_id":review_sql.review_id,
        "review_text": review_kr.review,
        "sentences": [
            sentence.to_dict() for sentence in review_kr.sentences
        ]
    }
    return review_data

def get_reviews_by_user_application(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    query = select(user_reviews_application_association.c.review_id).where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id)
    )
    results = db.session.execute(query).fetchall()
    user_reviews_ids = [result[0] for result in results]
    reviews_request = [{"reviewId":get_review_by_id(id).review_id} for id in user_reviews_ids]
    reviews_kr = get_reviews_from_knowledge_repository(reviews_request)

    data = {
        "application" : {
            "id" : application_id,
            "name" : application_entity.name.replace('_', " ")
        },
        "reviews" : []
    }
    for review_kr in reviews_kr:
        review_data = {
            "review_id":review_kr.reviewId,
            "review_text": review_kr.review
        }
        data["reviews"].append(review_data)
    return data

def get_reviews_by_user(user_id, page, page_size):
    total_reviews_query = db.session.query(func.count()).select_from(user_reviews_application_association).\
        filter(user_reviews_application_association.c.user_id == user_id)
    
    total_reviews_count = db.session.execute(total_reviews_query).scalar()
    if (page is not None and page_size is not None):
        offset = (page - 1) * page_size
        query = select(
            user_reviews_application_association.c.review_id,
            user_reviews_application_association.c.application_id
        ).where(
            user_reviews_application_association.c.user_id == user_id
        ).limit(page_size).offset(offset)
    else:
        query = select(
            user_reviews_application_association.c.review_id,
            user_reviews_application_association.c.application_id
        ).where(
            user_reviews_application_association.c.user_id == user_id
        )
    
    results = db.session.execute(query).fetchall()
    
    reviews_entities = [db.session.query(Review).filter_by(id=result[0]).first() for result in results]
    application_ids = [result[1] for result in results]

    reviews_request = [{"reviewId": review.review_id} for review in reviews_entities]
    reviews_kr = get_reviews_from_knowledge_repository(reviews_request)
    
    reviews = []
    for review_kr, application_id in zip(reviews_kr, application_ids):
        app = review_kr.applicationId.replace('_', " ")
        review_data = {
            "app_id": application_id,
            "app_name": app,
            "review_id": review_kr.reviewId,
            "review": review_kr.review,
            "date": review_kr.date
        }
        reviews.append(review_data)

    total_pages = 0
    if (page is not None and page_size is not None):
        total_pages = math.ceil(total_reviews_count / page_size)
    
    return {'reviews': reviews, 'total_pages': total_pages}

def has_user_review(user_id, application_id, review_id):
    query = user_reviews_application_association.select().where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id) &
        (user_reviews_application_association.c.review_id == review_id)
    )
    result = db.session.execute(query).fetchone()
    return result is not None



        