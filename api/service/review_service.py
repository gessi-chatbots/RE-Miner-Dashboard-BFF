from api import db
from api.models import Review, user_reviews_application_association
from sqlalchemy import select, delete, exc, func
from typing import List
from datetime import date, datetime
from dotenv import load_dotenv
import api.service.user_service as user_service
import api.service.mobile_application_service as mobile_application_service
import api.exceptions as api_exceptions
import requests
import nltk
import uuid
import json
import os
import math
import logging

api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)
load_dotenv()
# API_ROUTE = os.environ["KNOWLEDGE_REPOSITORY_URL"] + os.environ.get("KNOWLEDGE_REPOSITORY_API") + os.environ["KNOWLEDGE_REPOSITORY_API_VERSION"] + os.environ["KNOWLEDGE_REPOSITORY_REVIEWS_API"]  
API_ROUTE = os.environ.get("KNOWLEDGE_REPOSITORY_URL", "http://localhost:3003") + os.environ.get("KNOWLEDGE_REPOSITORY_REVIEWS_API","/reviews")


class LanguageModelDTO:
    def __init__(self, modelName: str):
        self.modelName = modelName

    def to_dict(self):
        return {
            "modelName": self.modelName,
        }


class FeatureDTO:
    def __init__(self, feature: str, languageModel: LanguageModelDTO):
        self.feature = feature
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "feature": self.feature,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
    
class PolarityDTO:
    def __init__(self, polarity: str, languageModel: LanguageModelDTO):
        self.polarity = polarity
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "polarity": self.polarity,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
    
class TypeDTO:
    def __init__(self, type: str, languageModel: LanguageModelDTO):
        self.type = type
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "type": self.type,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }
    
class TopicDTO:
    def __init__(self, topic: str, languageModel: LanguageModelDTO):
        self.topic = topic
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "topic": self.topic,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
        }

class SentimentDTO:
    def __init__(self, sentiment: str, languageModel: LanguageModelDTO):
        self.sentiment = sentiment
        self.languageModel = languageModel

    def to_dict(self):
        return {
            "sentiment": self.sentiment,
            "languageModel": self.languageModel.to_dict() if self.languageModel is not None else None,
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
    def __init__(self, id: str, applicationId: str, review: str, date: date, sentences: List[SentenceDTO]):
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


class ReviewFeatureDTO:
    def __init__(self,
                 appId: str,
                 reviewId: str,
                 review: str,
                 features: List[FeatureDTO],
                 emotions: List[SentimentDTO],
                 polarities: List[PolarityDTO],
                 types: List[TypeDTO],
                 topics: List[TopicDTO]):
        self.appId = appId
        self.reviewId = reviewId
        self.review = review
        self.features = features
        self.emotions = emotions
        self.polarities = polarities
        self.types = types
        self.topics = topics

    def to_dict(self):
        return {
            "appPackage": self.appId,
            "reviewId": self.reviewId,
            "review": self.review,
            "emotions": [emotion.to_dict() for emotion in self.emotions],
            "features": [feature.to_dict() for feature in self.features],
            "polarities": [polarity.to_dict() for polarity in self.polarities],
            "types": [type.to_dict() for type in self.types],
            "topics": [topic.to_dict() for topic in self.topics]
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
    application_entity = mobile_application_service.get_application_by_id(application_id)
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


def get_reviews_from_knowledge_repository(reviews):
    try:
        if isinstance(reviews, str):  # If it's a single string, convert it to a list
            reviews_json = [reviews]
        elif isinstance(reviews, list):  # If it's already a list, keep it as is
            reviews_json = reviews
        else:
            raise ValueError("Invalid input: reviews must be a list or a string")

        response = requests.get(
            API_ROUTE + '/list',
            json=reviews_json
        )

        if response.status_code == 200:
            return [extract_review_dto_from_json(review_json) for review_json in response.json()]
        else:
            raise api_exceptions.KGRReviewsNotFoundException

    except requests.exceptions.ConnectionError as e:
        print(f"error {e}")
        raise api_exceptions.KGRConnectionException()


def get_filtered_reviews_from_knowledge_repository(filters, page, page_size):
    try:
        features = filters.get('features', [])
        if not isinstance(features, list):
            features = [features]

        features_pascal_case = [convert_to_pascal_case(feature) for feature in features]

        payload = {
            key: value
            for key, value in {
                "app_id": filters.get("app_id", None),
                "features": features_pascal_case if features_pascal_case else None,
                "topic": filters.get("topic", None),
                "emotion": filters.get("emotion", None),
                "polarity": filters.get("polarity", None),
                "type": filters.get("type", None),
            }.items()
            if value is not None
        }
        # Prepare query parameters
        query_params = {"page": page, "size": page_size}

        response = requests.post(
            API_ROUTE + "/by-descriptors",
            params=query_params,
            json=payload,
        )

        # Process the response

        if response.status_code == 200:
            response_json = response.json()

            # Extract pagination metadata
            current_page = response_json.get('currentPage', 0)
            total_pages = response_json.get('totalPages', 0)
            total_elements = response_json.get('totalElements', 0)
            page_size = response_json.get('pageSize', 10)
            last_page = response_json.get('last', False)

            # Extract the actual review data
            review_response_dtos = []
            reviews_json = response_json.get('content', [])  # Ensure you get content, not full response
            for review_json in reviews_json:
                review_response_dtos.append(extract_review_w_descriptors_dto_from_json(review_json).to_dict())

            # Return the full paginated response
            return {
                "content": review_response_dtos,
                "currentPage": current_page,
                "totalPages": total_pages,
                "totalElements": total_elements,
                "pageSize": page_size,
                "last": last_page
            }

    except requests.exceptions.ConnectionError as e:
        print(f"error {e}")
        raise api_exceptions.KGRConnectionException()

def convert_to_pascal_case(feature):
    return ''.join(word.capitalize() for word in feature.split())

def get_feature_reviews_from_knowledge_repository(app_id, features):
    try:
        if not isinstance(features, list):
            features = [features]

        features_pascal_case = [convert_to_pascal_case(feature) for feature in features]
        payload = {
            "app_id": app_id,
            "features": features_pascal_case
        }
        response = requests.post(
            API_ROUTE + '/by-features',
            json=payload
        )

        if response.status_code == 200:
            review_response_dtos = []
            for review_json in response.json():
                review_response_dtos.append(extract_review_w_descriptors_dto_from_json(review_json).to_dict())
            return review_response_dtos
        elif response.status_code in (404, 204):
            raise api_exceptions.KGRReviewsNotFoundException
    except requests.exceptions.ConnectionError as e:
        print(f"error {e}")
        raise api_exceptions.KGRConnectionException()


def extract_review_w_descriptors_dto_from_json(review_feature_json):
    id = review_feature_json.get('reviewId', "N/A")
    body = review_feature_json.get('review', "N/A")
    appId = review_feature_json.get('appId', "N/A")

    features = []
    feature_dtos = review_feature_json.get('featureDTOs', [])
    for feature_dto_json in feature_dtos:
        feature = feature_dto_json.get('feature')
        model = feature_dto_json.get('languageModel').get('modelName')
        feature_dto = FeatureDTO(feature=feature, languageModel=LanguageModelDTO(model))
        features.append(feature_dto)

    emotions = []
    emotion_dtos = review_feature_json.get('sentimentDTOs', [])
    for emotion_dto_json in emotion_dtos:
        sentiment = emotion_dto_json.get('sentiment')
        language_model = emotion_dto_json.get('languageModel')
        model = language_model.get('modelName') if language_model is not None else None
        emotion_dto = SentimentDTO(sentiment=sentiment, languageModel=LanguageModelDTO(model))
        emotions.append(emotion_dto)

    polarities = []
    polarity_dtos = review_feature_json.get('polarityDTOs', [])
    for polarity_dto_json in polarity_dtos:
        polarity = polarity_dto_json.get('polarity')
        language_model = polarity_dto_json.get('languageModel')
        model = language_model.get('modelName') if language_model is not None else None
        polarity_dto = PolarityDTO(polarity=polarity, languageModel=LanguageModelDTO(model))
        polarities.append(polarity_dto)

    types = []
    type_dtos = review_feature_json.get('typeDTOs', [])
    for type_dto_json in type_dtos:
        type = type_dto_json.get('type')
        language_model = type_dto_json.get('languageModel')
        model = language_model.get('modelName') if language_model is not None else None
        type_dto = TypeDTO(type=type, languageModel=LanguageModelDTO(model))
        types.append(type_dto)

    topics = []
    topic_dtos = review_feature_json.get('topicDTOs', [])
    for topic_dto_json in topic_dtos:
        topic = topic_dto_json.get('topic')
        language_model = topic_dto_json.get('languageModel')
        model = language_model.get('modelName') if language_model is not None else None
        topic_dto = TopicDTO(topic=topic, languageModel=LanguageModelDTO(model))
        topics.append(topic_dto)

    review_response_dto = ReviewFeatureDTO(appId=appId,
                                           reviewId=id,
                                           review=body,
                                           features=features,
                                           emotions=emotions,
                                           polarities=polarities,
                                           types=types,
                                           topics=topics)
    return review_response_dto

def extract_review_dto_from_json(review_json):
    app_identifier = review_json.get('applicationId')
    id = review_json.get('reviewId')
    body = review_json.get('review')
    sentences_json = review_json.get('sentences')
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
    review_response_dto = ReviewResponseDTO(id=id, applicationId=app_identifier, review=body, date=date,
                                            sentences=sentences)
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
    if not review.sentences or len(review.sentences) == 0:
        review.sentences = [
            SentenceDTO(id=f"{review.reviewId}_{i + 1}", featureData=None, sentimentData=None, text=sentence)
            for i, sentence in enumerate(sentences)
        ]
    else:
        try:
            for index, sentence in enumerate(sentences):
                review.sentences[index].text = sentence
        except IndexError:  # NLTK sometimes splits randomly
            sentence_id = f"{review.reviewId}_{index + 1}"
            review.sentences.append(SentenceDTO(id=sentence_id, featureData=None, sentimentData=None, text=sentence))


def send_to_hub_for_analysis(reviews, feature_model, sentiment_model, polarity_model, type_model, topic_model, hub_version):
    endpoint_url = os.environ.get('HUB_URL', 'http://127.0.0.1:3002') + '/analyze'
    
    api_logger.info(f"[{datetime.now()}]: HUB URL {endpoint_url}")
    
    # Create a dictionary of model parameters, filtering out None values
    model_params = {
        'feature_model': feature_model,
        'sentiment_model': sentiment_model,
        'polarity_model': polarity_model,
        'type_model': type_model,
        'topic_model': topic_model
    }
    params = {k: v for k, v in model_params.items() if v is not None}
    
    # Add parameters to URL if any exist
    if params:
        param_strings = [f"{k}={v}" for k, v in params.items()]
        endpoint_url += '?' + '&'.join(param_strings)
    
    if hub_version == 'v0':
        reviews_dict = [review.to_dict() for review in reviews]
    else:
        reviews_dict = reviews
    response = requests.post(endpoint_url, json=reviews_dict)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        api_logger.info(f"[{datetime.now()}]: HUB unnexpected response {response.status_code} {response}")
        raise api_exceptions.HUBException()


def analyze_reviews(reviewsIds, feature_model, sentiment_model, polarity_model, type_model, topic_model):
    # validate_reviews(user_id, reviewsIds)
    api_logger.info(f"[{datetime.now()}]: Get reviews from KG")
    kr_reviews = get_reviews_from_knowledge_repository(reviewsIds)
    if kr_reviews is None:
        raise api_exceptions.KGRReviewsNotFoundException()
    for kr_review in kr_reviews:
        check_review_splitting(kr_review)
    hub_response = send_to_hub_for_analysis(kr_reviews, feature_model, sentiment_model, polarity_model, type_model, topic_model, 'v0')
    # TODO create dtos with id and the analysis results to reduce statements in kg repo
    insert_reviews_in_kg(hub_response['analyzed_reviews'])
    return hub_response['analyzed_reviews']


def analyze_multiprocessing(reviewsIds, feature_model, sentiment_model):
    # validate_reviews(user_id, reviewsIds)
    kr_reviews = get_reviews_from_knowledge_repository(reviewsIds)
    if kr_reviews is None:
        raise api_exceptions.KGRReviewsNotFoundException()
    sentences_dict_list = []
    for kr_review in kr_reviews:
        check_review_splitting(kr_review)
        for sentence in kr_review.sentences:
            sentences_dict_list.append({"id": sentence.id, "sentence": sentence.text})
    hub_response = send_to_hub_for_analysis(sentences_dict_list, feature_model, sentiment_model, 'v1')

    for sentence in hub_response:
        sentence_id = sentence.get('id')
        review_id = sentence_id.split('_')[0]
        for kr_review in kr_reviews:
            if kr_review.reviewId == review_id:
                for kr_sentence in kr_review.sentences:
                    if kr_sentence.id == sentence_id:
                        if sentence.get('featureData') is not None and sentence.get('featureData').get(
                                'feature') is not None:
                            kr_sentence.featureData = FeatureDTO(sentence.get('featureData').get('feature'))
                        if sentence.get('sentimentData') is not None and sentence.get('sentimentData').get(
                                'sentiment') is not None:
                            kr_sentence.sentimentData = SentimentDTO(sentence.get('sentimentData').get('sentiment'))
    dict_reviews = [kr_review.to_dict() for kr_review in kr_reviews]
    insert_reviews_in_kg(dict_reviews)
    return dict_reviews


def insert_reviews_in_kg(reviews):
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            API_ROUTE + '/',
            headers=headers,
            json=(reviews if isinstance(reviews, list) else [reviews])
        )
        if response.status_code == 201:
            return response.json
        else:
            print(f"error {response}")
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e:
        print(f"error {e}")
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
        raise api_exceptions.ReviewNotFoundException(user_id=user_id, application_id=application_id,
                                                     review_id=review_id)
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
        create_review(user_id, application_name, review['reviewId'])  #TODO handle exception: review does not have id


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


def get_review(application_id, review_id):
    review_kr = get_reviews_from_knowledge_repository(review_id)
    rev = review_kr[0] # just the first review
    add_sentences_to_review(rev)
    review_data = {
        "application": {
            "id": application_id,
            "name": rev.applicationId
        },
        "id": rev.reviewId,
        "review_id": rev.reviewId,
        "review_text": rev.review,
        "sentences": [
            sentence.to_dict() for sentence in rev.sentences
        ]
    }
    return review_data


def get_reviews_by_user_application(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    application_entity = mobile_application_service.get_application_by_id(application_id)
    validate_user_and_application(user_entity, application_entity)
    query = select(user_reviews_application_association.c.review_id).where(
        (user_reviews_application_association.c.user_id == user_id) &
        (user_reviews_application_association.c.application_id == application_id)
    )
    results = db.session.execute(query).fetchall()
    user_reviews_ids = [result[0] for result in results]
    reviews_request = [get_review_by_id(id).review_id for id in user_reviews_ids]
    reviews_kr = get_reviews_from_knowledge_repository(reviews_request)

    data = {
        "application": {
            "id": application_id,
            "name": application_entity.name.replace('_', " ")
        },
        "reviews": []
    }
    for review_kr in reviews_kr:
        review_data = {
            "review_id": review_kr.reviewId,
            "review_text": review_kr.review
        }
        data["reviews"].append(review_data)
    return data


def get_reviews_by_user(user_id, page, page_size):
    total_reviews_query = db.session.query(func.count()).select_from(user_reviews_application_association). \
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

    reviews_request = [review.review_id for review in reviews_entities]
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


def get_reviews_by_filters(filters, page, page_size):
    reviews_kr = get_filtered_reviews_from_knowledge_repository(filters, page, page_size)
    return reviews_kr
