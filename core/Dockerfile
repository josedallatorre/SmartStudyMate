FROM python:3.8

RUN apt-get update \
  && apt-get install -y --force-yes nano python3-pip gettext chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev ffmpeg git libmagic-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip
RUN pip install --upgrade pip

# Install curl for healthchecks
RUN apt update && apt install curl

COPY . .

# Set Flask app environment variable and upgrade pip
ENV FLASK_APP=app.py
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "app.py"]
