FROM jazzdd/alpine-flask:python3

RUN apk add --no-cache py3-lxml

COPY .env /app
COPY fullcalendar_event.py /app
COPY ews_to_fullcalendar.py /app
COPY app.py /app
COPY crontabs/root /var/spool/cron/crontabs/root
COPY requirements.txt /app
COPY sync.sh /app
COPY entrypoint.sh /app

ENTRYPOINT ["/app/entrypoint.sh"]
