FROM python:3.6

RUN adduser --disabled-password predictor

WORKDIR /home/predictor

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP app.py

RUN chown -R predictor:predictor ./
USER predictor

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]