class UnknownException(Exception):
    code = 500
    message = "Unexpected server error"

class HUBException(Exception):
    code = 500
    message = "There was an error in the RE-Miner HUB"


class UserNotFoundException(Exception):
    code = 404
    message = "User not found"


class KGRReviewsNotFoundException(Exception):
    code = 404
    message = "Not found any reviews in the KGR"

class ApplicationNotFoundException(Exception):
    code = 404
    message = "Application not found"

class ReviewNotFoundException(Exception):
    def __init__(self, user_id, review_id, application_id):
        self.review_id = review_id
        self.application_id = application_id
        self.user_id = user_id
        self.code = 404
        self.message = f"Review: {self.review_id}, does not exist in Application {self.application_id} for User {self.user_id}"

class UserIntegrityException(Exception):
    code = 400
    message = "An User with the given email is already registered"

class UnauthorizedUserException(Exception):
    code = 401
    message = "Not an authorized user for doing that action"

class ReviewNotFromUserException(Exception):
    def __init__(self, review_id, user_id):
        self.review_id = review_id
        self.code = 401
        self.user_id = user_id
        self.message = f"Review: {self.review_id}, does not belong to User {user_id}"

class KGRException(Exception):
    code = 500
    message = "There was an error in the Knowledge Graph Repository"

class KGRConnectionException(Exception):
    code = 503
    message = "There was an error connecting to the Knowledge Graph Repository"
class KGRApplicationNotFoundException(Exception):
    code = 404
    message = "The application does not exist in the Knowledge Graph"

class KGRApplicationsNotFoundException(Exception):
    code = 204
    message = "No applications found in the Knowledge Graph"
