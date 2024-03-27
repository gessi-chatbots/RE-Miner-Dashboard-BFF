import uuid
import api.service.user_service as user_service
import api.service.review_service as review_service
import api.exceptions as api_exceptions
import requests
import json
import os
from api import db
from api.models import Application, User, user_reviews_application_association
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

def get_applications(user_id):
    user = user_service.get_user_by_id(user_id)
    applications = user.applications.all()
    application_list = []
    for app in applications:
        application = {
            'data': app.json(),
            'reviews': []
        }
        for rev in app.reviews:
            application['reviews'].append(rev.json())
        application_list.append(application)
    return application_list

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
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/applications'
        response = requests.post(
            url,
            headers=headers,
            json=(applications if isinstance(applications, list) else [applications])
        )
        if response.status_code == 201:
            return response.json
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


def is_application_from_user(user_id, application_id):
    user_entity = user_service.get_user_by_id(user_id)
    if user_entity.applications:
        return application_id in [application.id for application in user_entity.applications]
    else: 
        return False

def get_applications_from_directory():
    try:
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + '/graph-db-api/applications/names'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise api_exceptions.KGRApplicationsNotFoundException
    except requests.exceptions.ConnectionError as e: 
        raise api_exceptions.KGRConnectionException(e)

def get_application_from_directory(app_name):
    app_name_sanitized = app_name.replace(" ", "_")
    try:
        url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + f'/graph-db-api/applications/{app_name_sanitized}'
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
            url = os.environ.get('KNOWLEDGE_REPOSITORY_URL', 'http://127.0.0.1:3003') + f'/graph-db-api/applications/{app_name}'
            response = requests.get(url)
            if response.status_code == 200:
                app_data = response.json()
                inserted_app = insert_application_in_sql_db(user_id, app_data)
                return inserted_app.json()
            else:
                raise api_exceptions.KGRException()
        except requests.exceptions.ConnectionError as e: 
            raise api_exceptions.KGRConnectionException(e)
    