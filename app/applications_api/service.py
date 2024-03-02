from app import db
from app.models import Application
import uuid
import app.users_api.service as users_api_service
import app.reviews_api.service as review_api_service
from sqlalchemy.exc import IntegrityError

def update_application(user_id, application_data):
    application_name = application_data['app_name']
    review_api_service.process_application_reviews(user_id, 
                                                   application_name, 
                                                   application_data.get('reviews', []))
    return Application(name=application_name)
   
def save_application_in_sql_db(user_id, application_data):
    user = users_api_service.get_user_by_id(user_id)
    new_application = create_new_application(user_id, application_data)
    user.applications.append(new_application)
    db.session.add(user)
    return new_application
    

def process_application(user_id, application_data):
    processed_application = save_application_in_sql_db(user_id, application_data)
    # save_application_in_graph_db(application)
    return processed_application.json()

def get_application_by_name(name): 
    return db.session.query(Application).filter_by(name=name).one_or_none()

def get_application_by_id(id): 
    return db.session.query(Application).filter_by(id=id).one_or_none()

def create_new_application(user_id, application_data):
    application_id = str(uuid.uuid4())
    application_name = application_data['app_name']
    try:
        new_application = Application(id = application_id, name=application_name)
        db.session.add(new_application)
        review_api_service.process_application_reviews(user_id, 
                                    application_name, 
                                    application_data.get('reviews', []))
        return new_application
    except IntegrityError as e:
        db.session.rollback()


def process_applications(user_id, applications):
    processed_applications = []
    try:
        for application_data in applications:
            processed_applications.append(process_application(user_id, application_data))
        db.session.commit()
        return processed_applications
    except IntegrityError as e:
        print(e)
        db.session.rollback()

# TODO do it without user_id and use user
def is_application_from_user(application_id, user_id):
    user_entity = users_api_service.get_user_by_id(user_id)
    if user_entity.applications:
        return application_id in [application.id for application in user_entity.applications]
    else: 
        return False

def get_all_user_applications(user_id):
    user = users_api_service.get_user_by_id(user_id)
    applications = user.applications.all()
    application_list = {
        "applications": [{'application_data': app.json()} for app in applications]
    }
    return application_list

def edit_application(application):
    return None

def delete_application(application_id):
    application_entity = get_application_by_id(application_id)
    if application_entity:
        db.session.delete(application_entity)
        db.session.commit()
    

def get_application(application_id):
    application_entity = get_application_by_id(application_id)
    application_data = {
        "application": {
            "application_data": application_entity.json(),
            "reviews": [{"review": review.json()} for review in application_entity.reviews]
        }
    }
    return application_data
