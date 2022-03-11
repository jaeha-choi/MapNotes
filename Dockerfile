# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN chmod +x ./start.sh
COPY . /code/

# save for later
EXPOSE 8080
CMD [ "./start.sh" ]
