from .models import Application, db
from flask import jsonify
from ..reviews_api.service import process_application_reviews, get_review_by_id
from ..users_api.service import get_user_by_id
from sqlalchemy.exc import IntegrityError

def update_application(application_data, application_entity):
    process_application_reviews(application_data.get('app_name'), 
                                application_data.get('reviews', []))
    
    new_application_reviews = application_data.get('reviews', [])
    
    for new_application_review in new_application_reviews:
        new_review_id = new_application_review.get('reviewId')
        # We check if the review is already saved in the database
        review_entity = get_review_by_id(new_review_id)
        if review_entity and new_review_id not in [review.id for review in application_entity.reviews]:
            application_entity.reviews.append(review_entity)     

def create_new_application(application):
    try:
        process_application_reviews(application.get('app_name'), 
                                    application.get('reviews', []))
        application_data = {
            'name': application.get('app_name')
        }
        new_application = Application(**application_data)
        application_reviews = application.get('reviews', [])
        for application_review in application_reviews:
            review_entity = get_review_by_id(application_review.get('reviewId'))
            if review_entity:
                new_application.reviews.append(review_entity)           
        db.session.add(new_application)
    except IntegrityError as e:
        db.session.rollback()

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

def process_applications(user_id, applications):
    try:
        user = get_user_by_id(user_id)
        for application in applications:
            application_name = application.get('app_name')
            process_application(application)
            if not is_application_from_user(application_name, user.id):
                user.applications.append(get_application_by_name(application_name))
        db.session.commit()   
    except IntegrityError as e:
        print(e)
        db.session.rollback()

def is_application_from_user(application_name, user_id):
    user = get_user_by_id(user_id)
    return application_name in [application.name for application in user.applications]

def get_all_user_applications(user_id):
    user = get_user_by_id(user_id)
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
