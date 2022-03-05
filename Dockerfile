# syntax=docker/dockerfile:1

FROM python:3.10.0-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD [ "python", "main.py" ]
