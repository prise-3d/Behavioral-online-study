# Django Web expe

## Description

Web site which contains experimentss on synthesis images (perception of noise). 

## Installation

### 1. Manually

#### Requirements

You need to have python, pip

```
pip install -r requirements.txt
```

Initialize the database with the following command :

```
python manage.py migrate
```

Add your own super user admin credentials:
```
cp credentials.example.json credentials.json
```

```json
{
    "username":"username",
    "email":"",
    "password":"pass"
}
```

Add your own configuration application:
```
cp expe/config.example.py expe/config.py
```

#### Run server

Run the server :

```
python manage.py runserver
```

or if you want to make it listen on a specific port number :

```
python manage.py runserver 8080
```

### 2. Using docker (recommended)

First, you need to add your own user admin credentials if you wished:
```
cp credentials.example.json credentials.json
```

You can use make commands:

```
make build
```

```
make run
```

Or simply:

```
make deploy
```

Will run `build` and `run` commands at once.

You also have `stop`, `remove`, `clean` commands:
- `stop`: stop current container instance if exists
- `remove`: stop and remove container instance if exists
- `clean`: remove docker image if exists

## Configuration

Create your own admin user:
```
python manage.py createsuperuser
```

You can now access `/admin/results` route with your credentials in order to download experiments results.

<hr />

Run the application:

```
python manage.py runserver
```

or using docker:

```
docker-compose up
```


## Create your experimentss

See [DOCUMENTATION.md](DOCUMENTATION.md). This documentation explains how to create your own experiments.

## How to contribute ?

This project uses [git-flow](https://danielkummer.github.io/git-flow-cheatsheet/) to improve cooperation during the development.

For each feature, you have to create a new git flow feature branch.

## Licence

[MIT](LICENSE)
