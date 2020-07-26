FROM python:3.5-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

LABEL maintainer="Utkarsh Dhawan <utkarsh.dhawan@exportify.in>"

CMD gunicorn -b 0.0.0.0:5000 wsgi:app --access-logfile '-'
