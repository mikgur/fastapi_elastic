FROM python:3.8

WORKDIR /app

RUN apt update && \
    apt install wget && \
    mkdir /var/log/wb

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /app
WORKDIR /

CMD [ "python", "-m", "app.telegram_bot" ]