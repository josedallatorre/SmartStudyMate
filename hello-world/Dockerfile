FROM python:3.8-alpine

WORKDIR /app

RUN apk add curl

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py

CMD ["python", "app.py"]
