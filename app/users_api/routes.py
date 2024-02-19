from . import users_api_bp
from . import users_api_logger
from datetime import datetime
@users_api_bp.route("/register")
def register_user():
    users_api_logger.info(f"[{datetime.now()}]Tryout") 
    return 'first commit'