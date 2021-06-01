FROM python:3.6.9

COPY . /usr/src/app
WORKDIR /usr/src/app

# Server port
EXPOSE 8000

RUN apt-get update

# Install dependencies and prepare project
RUN python --version
RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate

# create super user admin automatically
RUN bash create_admin.sh

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]