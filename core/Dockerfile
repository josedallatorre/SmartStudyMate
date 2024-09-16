FROM python:3.8

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
