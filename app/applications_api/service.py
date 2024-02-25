from .models import Application

def save_application_in_sql_db(application):
    return None

# TODO
def save_application_in_graph_db(application):
    return None

def process_application(application):
    save_application_in_sql_db(application)
    save_application_in_graph_db(application)

def process_applications(applications):
    for application in applications:
        print(application)
        process_application(application)