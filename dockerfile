FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app .

COPY requirements.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN sed -i '/psycopg2-binary/d' requirements.txt

RUN pip install -r requirements.txt

ENV DJANGO_ALLOWED_HOSTS="[]" \
    DJANGO_CSRF_TRUSTED_ORIGINS="[]" \
    BUILD_RUN=1

RUN python manage.py collectstatic --noinput

ENV BUILD_RUN=0

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["bash", "/app/entrypoint.sh"]

CMD ["--workers", "3"]
