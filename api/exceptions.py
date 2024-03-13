class ReviewNotFound(Exception):
    code = 404
    message = "Review not found"

class UnknownException(Exception):
    code = 500
    message = "Unexpected server error"

class UserNotFoundException(Exception):
    code = 404
    message = "User not found"

class ApplicationNotFoundException(Exception):
    code = 404
    message = "Application not found"

class ReviewNotFoundException(Exception):
    code = 404
    message = "Application not found"

class UserIntegrityException(Exception):
    code = 400
    message = "An User with the given email is already registered"

class UnauthorizedUserException(Exception):
    code = 401
    message = "Not an authorized user for doing that action"

class ReviewNotFromUserException(Exception):
    def __init__(self, review_id):
        self.review_id = review_id
        self.code = 401
        self.message = f"Review: {self.review_id}, does not belong to user"

class KGRException(Exception):
    code = 500
    message = "There was an error in the Knowledge Graph Repository"

class KGRConnectionException(Exception):
    code = 503
    message = "There was an error connecting to the Knowledge Graph Repository"
