from . import users_api_bp

@users_api_bp.route("/register")
def register_user(): 
    return 'first commit'