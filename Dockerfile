FROM python:3.8.0a3-alpine3.9
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 8000
RUN ls
CMD python app.py
