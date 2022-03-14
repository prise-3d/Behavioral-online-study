Installation
============


Install requirements
~~~~~~~~~~~~~~~~~~~~

Installing prerequisites

- git_
- Python_ (>= 3.7)


You need to clone this repository:

.. code:: bash

   git clone https://github.com/prise-3d/behavioral-online-experiment.git

.. _git: https://git-scm.com/
.. _Python: https://www.python.org/

With your python version (ideally python >= 3.7), you can the following required modules:

.. code:: bash
   
   pip install -r requirements.txt


You may need to install sqlite3 on your system. For Debian based system:

.. code::

   apt update
   apt install sqlite3


.. warning::

   It may required a new Python install.


Configure server
~~~~~~~~~~~~~~~~

Add your own super user admin credentials:

.. code:: bash

   cp credentials.example.json credentials.json
   

.. code-block:: json

   {
      "username":"username",
      "email":"",
      "password":"pass"
      "secret_key": "******"
   }

You can generate and replace the secret key param:

.. code:: python

   from django.core.management.utils import get_random_secret_key
   # print new random secret key
   print(get_random_secret_key())


.. caution:: 

   Django requires a secret key to securing signed data.

Database initialization
~~~~~~~~~~~~~~~~~~~~~~~

Initialize the database with the following command:

.. code:: bash

   python manage.py makemigrations
   python manage.py migrate


Then create the admin account:

.. code:: bash

   bash create_admin.sh

.. note::

   if you got a confirmation message that your administrator account has been created, everything is going well for the moment!


Run the web application
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   python manage.py runserver

.. note::
   The administrator interface is now available: ``http://127.0.0.1:8000/admin``.

Or on a specific port:

.. code:: bash

   python manage.py runserver 8080

Using docker
~~~~~~~~~~~~~~~~

First, you need to add your own user admin credentials wished:

.. code:: bash

   cp credentials.example.json credentials.json


Then, use make commands:

.. code:: bash

   make build
   make run


Or simply:

.. code:: bash

   make deploy


You also have ``stop``, ``remove``, ``clean`` commands:

- ``stop``: stop current container instance if exists
- ``remove``: stop and remove container instance if exists
- ``clean``: remove docker image if exists




