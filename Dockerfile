FROM python:3.9

WORKDIR /wsgi

COPY Pipfile Pipfile.lock /wsgi/

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

COPY . /wsgi

COPY wait-for-it.sh /wsgi/wait-for-it.sh
RUN chmod +x /wsgi/wait-for-it.sh

EXPOSE 3003

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0", "--port=3003"]
