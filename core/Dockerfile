FROM python:3.8

# upgrade pip
RUN pip install --upgrade pip

RUN apt-get update \
  && apt-get install -y --force-yes nano python3-pip gettext chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev ffmpeg git libmagic-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# get curl for healthchecks
RUN apt install curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot . .

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN export FLASK_APP=app.py
RUN "$VIRTUAL_ENV/bin/python" -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
