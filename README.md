# Behavioral online experiment


[![GitHub](https://img.shields.io/github/license/prise-3d/behavioral-online-experiment?style=flat)](https://github.com/prise-3d/behavioral-online-experiment/blob/master/LICENCE)


<p align="center">
    <img src="https://github.com/prise-3d/behavioral-online-experiment/blob/master/docs/source/_static/behavioral_logo.svg" alt="" width="55%">
</p>

## Description

This project is a framework for designing online behavioral experiment. It proposes a common base for all experiments using the Django Python web framework. The use of Python allows to easily integrate libraries on the application server that can be used for the experiment.

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

#### Credentials and configuration
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

#### Admin user creation

Create your own admin user:
```
python manage.py createsuperuser
```

You can now access `/admin/results` route with your credentials in order to download experiments results.
Note that the current proposed results page is an example.

#### Run the web application

Run the server :

```
python manage.py runserver
```

or if you want to make it listen on a specific port number :

```
python manage.py runserver 8080
```

### 2. Using docker (recommended)

First, you need to add your own user admin credentials wished:
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

## How to contribute ?

This project uses [git-flow](https://danielkummer.github.io/git-flow-cheatsheet/) to improve cooperation during the development.

For each feature, you have to create a new git flow feature branch.

## Licence

[MIT](LICENSE)
