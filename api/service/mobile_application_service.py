import uuid
import api.service.user_service as user_service
import api.service.review_service as review_service
import api.exceptions as api_exceptions
import requests
import logging
import os

from datetime import datetime
from api import db
from api.models import Application, User, user_reviews_application_association
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
import sys

api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
api_logger.addHandler(handler)
# api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]api.log'))
# API_ROUTE = os.environ.get("KNOWLEDGE_REPOSITORY_URL") + os.environ.get("KNOWLEDGE_REPOSITORY_API") + os.environ.get("KNOWLEDGE_REPOSITORY_API_VERSION") + os.environ.get("KNOWLEDGE_REPOSITORY_MOBILE_APPLICATIONS_API")  
API_ROUTE = os.environ.get("KNOWLEDGE_REPOSITORY_URL", "http://127.0.0.1:3003") + os.environ.get("KNOWLEDGE_REPOSITORY_MOBILE_APPLICATIONS_API", "/mobile-applications")  

def get_applications(user_id, page, page_size):
    user = user_service.get_user_by_id(user_id)
    applications_query = user.applications

    # Calculate offset based on page number and page size
    offset = (page - 1) * page_size

    # Fetch applications for the current page
    applications = applications_query.offset(offset).limit(page_size).all()

    total_count = applications_query.count()
    total_pages = (total_count + page_size - 1) // page_size

    application_list = []

    for app in applications:
        application = {
            'data': app.json(),
            'reviews': [rev.json() for rev in app.reviews]
        }
        clean_name = application['data']['name'].replace('_', ' ')
        application['data']['name'] = clean_name
        application_list.append(application)

    return application_list, total_pages


def update_application(user_id, application_data):
    application_name = application_data['app_name']
    review_service.process_application_reviews(user_id, 
                                                   application_name, 
                                                   application_data.get('reviews', []))
    return Application(name=application_name)

def get_application(user_id, application_id):
    user = User.query.get(user_id)
    if user:
        application = user.applications.filter_by(id=application_id).first()
        if application:
            app_kg = get_application_from_directory(application.name)
            application_data = {
                "data": app_kg,
                "user_reviews": [{"review": review.json()} for review in application.reviews]
            }
            return application_data
        else: 
            return None
        
def get_application_features(application_id):
    app = get_application_by_id(application_id)
    app_name_sanitized = app.name.replace(" ", "_")
    try:
        response = requests.get(API_ROUTE)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise api_exceptions.KGRApplicationNotFoundException()
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException(e)

def delete_application(user_id, application_id):
    user = User.query.get(user_id)
    if user:
        application = user.applications.filter_by(id=application_id).first()
        if application:
            db.session.execute(
                delete(user_reviews_application_association).where(
                    (user_reviews_application_association.c.user_id == user_id) &
                    (user_reviews_application_association.c.application_id == application_id)
                )
            )
            db.session.delete(application)
            db.session.commit()
            return True
        else:
            raise api_exceptions.ApplicationNotFoundException
    else: 
        raise api_exceptions.UserNotFoundException

def get_application_by_name(name): 
    return db.session.query(Application).filter_by(name=name).one_or_none()

def get_application_by_id(id): 
    return db.session.query(Application).filter_by(id=id).one_or_none()

def save_application_in_sql_db(user_id, application_data):
    user = user_service.get_user_by_id(user_id)
    new_application = insert_application_in_sql_db(user_id, application_data)
    db.session.add(user)
    return {
        "id": new_application.id,
        "name": new_application.name
    }
    
def insert_application_in_sql_db(user_id, application_data):
    application_id = str(uuid.uuid4())
    application_name = ""
    # TODO fix formats
    if ('app_name' not in application_data and 'name' in application_data):
        application_name = application_data['name']
    if ('app_name' in application_data and 'name' not in application_data):        
        application_name = application_data['app_name']
    try:
        new_application = Application(id = application_id, name=application_name)
        db.session.add(new_application)
        user = user_service.get_user_by_id(user_id)
        user.applications.append(new_application)
        db.session.commit()
        review_service.process_application_reviews(user_id, application_id, application_data.get('reviews', []))
        return new_application
    except IntegrityError as e:
        raise api_exceptions.UserIntegrityException()
    
def send_applications_to_kg(applications):
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            API_ROUTE + '/',
            headers=headers,
            json=(applications if isinstance(applications, list) else [applications])
        )
        if response.status_code == 201:
            return response.json
        else:
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException(e)
    
def get_kg_top_features(applications):
    try:
        applications = [app.replace(" ", "_") for app in applications]
        headers = {'Content-type': 'application/json'}
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/analysis/top-features'
        response = requests.post(
            url,
            headers=headers,
            json=(applications if isinstance(applications, list) else [applications])
        )
        if response.status_code == 200:
            transformed_response = [{'feature': item['featureName'], 'occurrences': item['occurrences']} for item in response.json()['topFeatures']]
            return transformed_response
        else:
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException(e)
    
def get_kg_top_sentiments(applications):
    try:
        applications = [app.replace(" ", "_") for app in applications]
        headers = {'Content-type': 'application/json'}
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/analysis/top-sentiments'
        api_logger.info(f"KG URL {url}")
        response = requests.post(
            url,
            headers=headers,
            json=(applications if isinstance(applications, list) else [applications])
        )
        if response.status_code == 200:
            transformed_response = [{'sentiment': item['sentimentName'], 'occurrences': item['occurrences']} for item in response.json()['topSentiments']]
            return transformed_response
        else:
            api_logger.warning(f"Response unwanted status {response} {response.status_code}")
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e:
        api_logger.error(f"error {e}")
        raise api_exceptions.KGRConnectionException(e)
    
def get_app_statistics(application, start_date="2020-01-01", end_date=None):
    try:
        app = get_application_by_id(application)
        app_name_sanitized = app.name.replace(" ", "_")
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + f'/graph-db-api/applications/{app_name_sanitized}/statistics'
        
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise api_exceptions.KGRException()
    except requests.exceptions.ConnectionError as e:
        raise api_exceptions.KGRConnectionException(e)
    
def process_applications(user_id, applications):
    send_applications_to_kg(applications)
    processed_applications = []
    try:
        for application_data in applications:
            processed_applications.append(save_application_in_sql_db(user_id, application_data))
        db.session.commit()
        return processed_applications
    except IntegrityError as e:
        db.session.rollback()
        raise api_exceptions.UnknownException

def get_top_sentiments(user_id, applications):
    return get_kg_top_sentiments(applications)



def get_top_features(user_id, applications):
    return get_kg_top_features(applications)


def is_application_from_user(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    if user_entity.applications:
        return application_id in [application.id for application in user_entity.applications]
    else: 
        return False

def get_applications_from_directory():
    try:
        url = API_ROUTE + '/basic-data'
        api_logger.info(url)
        response = requests.get(url)
        if response.status_code == 200:
            api_logger.info(response)
            if response.json is None:
                raise api_exceptions.KGRApplicationsNotFoundException
            return response.json()
        elif response.status_code == 404:
            raise api_exceptions.KGRApplicationsNotFoundException
    except requests.exceptions.ConnectionError as e: 
        api_logger.error(f"[{datetime.now()}]: KG Error {e}")
        raise api_exceptions.KGRConnectionException(e)

def get_application_from_directory(app_name):
    app_name_sanitized = app_name.replace(" ", "_")
    try:
        url = API_ROUTE + f'/{app_name_sanitized}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise api_exceptions.KGRApplicationNotFoundException()
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException(e)
    
def add_applications_from_directory_to_user(user_id, app_list):
    for app in app_list:
        try:
            app_name = app['app_name']
            url = API_ROUTE + f'/{app_name}'
            response = requests.get(url)
            if response.status_code == 200:
                app_data = response.json()
                inserted_app = insert_application_in_sql_db(user_id, app_data)
                return inserted_app.json()
            else:
                raise api_exceptions.KGRException()
        except requests.exceptions.ConnectionError as e: 
            raise api_exceptions.KGRConnectionException(e)
    