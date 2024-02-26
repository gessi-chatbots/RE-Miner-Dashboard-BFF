from .models import Application, db
import uuid
from ..reviews_api.service import process_application_reviews, get_review_by_id
from ..users_api.service import get_user_by_id
from sqlalchemy.exc import IntegrityError

def save_application_in_sql_db(application):
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
        print('App already exists rollbacking...')
        db.session.rollback()

# TODO
def save_application_in_graph_db(application):
    return None

def process_application(application):
    save_application_in_sql_db(application)
    save_application_in_graph_db(application)

def get_application_by_name(name): 
    return Application.query.filter_by(name=name).one_or_none()

def process_applications(user_id, applications):
    try:
        db.session.begin()
        user = get_user_by_id(user_id)
        for application in applications:
            # TODO check if there is a way to obtain the entity and not doing w & r
            process_application(application)
            user.applications.append(get_application_by_name(application.get('app_name')))
        db.session.commit()     
    except IntegrityError as e:
        db.session.rollback()

def is_application_from_user(application_name, user_id):
    user = get_user_by_id(user_id)
    return None

def get_all_user_applications(user_id):
    user = get_user_by_id
    return None