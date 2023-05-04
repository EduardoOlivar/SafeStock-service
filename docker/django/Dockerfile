FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirements_unix.txt .
RUN pip install -r requirements_unix.txt

COPY . .

EXPOSE 8000

COPY ./docker/django/django.sh ./django.sh

RUN chmod +x ./django.sh
ENTRYPOINT ["./django.sh"]