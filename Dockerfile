FROM jazzdd/alpine-flask:python3

COPY app.py /app
COPY ews_to_fullcalendar.py /app
copy requirements.txt /app
