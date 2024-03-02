from flask import jsonify

def validate_form(form): 
    if not form.validate():
        errors = {"errors": []}
        for field, messages in form.errors.items():
            for error in messages:
                errors["errors"].append({"field": field, "message": error})
        return jsonify(errors), 400
    
