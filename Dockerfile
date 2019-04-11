FROM python:3.8.0a3-alpine3.9
RUN apk add gcc python-dev libxml2-dev libxslt-dev musl-dev
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN ls
CMD gunicorn -b 0.0.0.0:5000 app:app
