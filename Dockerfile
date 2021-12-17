FROM python:3.10.1

VOLUME /app
WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt
