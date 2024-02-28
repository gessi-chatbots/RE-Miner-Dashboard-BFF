from app import db
from app.models import Application
from flask import jsonify
import app.users_api.service as users_api_service
import app.reviews_api.service as review_api_service
from sqlalchemy.exc import IntegrityError

def update_application(application_data, application_entity):
    review_api_service.process_application_reviews(application_data.get('app_name'), 
                                application_data.get('reviews', []))
    
    new_application_reviews = application_data.get('reviews', [])
    
    for new_application_review in new_application_reviews:
        new_review_id = new_application_review.get('reviewId')
        # We check if the review is already saved in the database
        review_entity = review_api_service.get_review_by_id(new_review_id)
        if review_entity and new_review_id not in [review.id for review in application_entity.reviews]:
            application_entity.reviews.append(review_entity)     

def save_application_in_sql_db(application_data):
    application_entity = get_application_by_name(application_data.get('app_name'))
    if application_entity is None: 
        create_new_application(application_data)
    else: 
        update_application(application_data, application_entity)
    

def process_application(application):
    save_application_in_sql_db(application)
    # save_application_in_graph_db(application)

def get_application_by_name(name): 
    return db.session.query(Application).filter_by(name=name).one_or_none()


def create_new_application(user_id, application_data):
    application_name = application_data['app_name']
    try:
        new_application = Application(name=application_name)
        db.session.add(new_application)
        review_api_service.process_application_reviews(user_id, 
                                    application_name, 
                                    application_data.get('reviews', []))
        return new_application
    except IntegrityError as e:
        db.session.rollback()


def process_applications(user_id, applications):
    try:
        user = users_api_service.get_user_by_id(user_id)
        for application_data in applications:
            application_entity = get_application_by_name(application_data.get('app_name'))
            if application_entity is None: 
                new_application = create_new_application(user_id, application_data)
                if not is_application_from_user(new_application.name, user.id):
                    user.applications.append(new_application)
            else: 
                update_application(application_data, application_entity)
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()

# TODO do it without user_id and use user
def is_application_from_user(application_name, user_id):
    user_entity = users_api_service.get_user_by_id(user_id)
    return application_name in [application.name for application in user_entity.applications]

def get_all_user_applications(user_id):
    user = users_api_service.get_user_by_id(user_id)
    applications = user.applications.all()
    application_list = [{'name': app.name} for app in applications]
    return jsonify(application_list)

def edit_application(application):
    return None

def delete_application(application_name):
    application_entity = get_application_by_name(application_name)
    if application_entity:
        db.session.delete(application_entity)
        db.session.commit()
    

def get_application(application_name):
    application_entity = get_application_by_name(application_name)
    application_data = {
        "name": application_entity.json(),
        "reviews": [review.json() for review in application_entity.reviews]
    }
    return application_data
