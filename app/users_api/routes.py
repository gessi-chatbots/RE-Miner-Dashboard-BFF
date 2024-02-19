from flask import request, redirect, url_for
from . import users_api_bp, users_api_logger
from .models import User, database
from datetime import datetime

@users_api_bp.post("/register")
def register():
    users_api_logger.info(f"[{datetime.now()}]: Register User") 
    name = request.form.get('name')
    family_name =  request.form.get('family_name')
    email = request.form.get('email')
    new_user = User(name=name, 
                    family_name=family_name, 
                    email=email) 
    database.session.add(new_user)
    database.session.commit()
    return redirect(url_for('.login'))
