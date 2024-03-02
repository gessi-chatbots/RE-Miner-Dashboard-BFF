class ReviewNotFound(Exception):
    code = 404
    message = "Review not found"

class UnknownException(Exception):
    code = 500
    message = "Unexpected server error"

class UserNotFoundException(Exception):
    code = 404
    message = "User not found"

class UserIntegrityException(Exception):
    code = 400
    message = "An User with the given email is already registered"
