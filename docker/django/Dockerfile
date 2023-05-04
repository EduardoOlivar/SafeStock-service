FROM python:3

ARG DB_IP
ARG DB_PORT
ARG SERVER_IP

ENV DB_IP=$DB_IP
ENV DB_PORT=$DB_PORT
ENV SERVER_IP=$SERVER_IP
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirements_unix.txt .
RUN pip install -r requirements_unix.txt

COPY . .

EXPOSE 8000

COPY ./docker/django/wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

COPY ./docker/django/django.sh ./django.sh
RUN chmod +x ./django.sh

COPY ./docker/django/run.sh ./run.sh
RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]