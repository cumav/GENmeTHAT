FROM python:3.6.0

RUN mkdir ./app
WORKDIR ./app
COPY . /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
EXPOSE 8000

ENTRYPOINT ["python3", "/app/manage.py", "runserver", "0.0.0.0:8000"]