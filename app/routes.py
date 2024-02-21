from . import app

@app.routes('/login', methods=['GET', 'POST'])
def login():
    return None