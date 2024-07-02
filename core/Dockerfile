FROM python:3.8
RUN apt-get update \
  && apt-get install -y --force-yes nano python3-pip gettext chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev ffmpeg git libmagic-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "provajose.py"]
