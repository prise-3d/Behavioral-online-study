======================================
A tour of Behavioral online experiment
======================================


This documentation will allow you to get to know the framework and the administrator interface. It will detail the concepts and the idea behind the abstraction for the creation of online experiments.

.. note:: 
    It is highly recommended to read this documentation in parallel with the administrator interface (which is available at ``http://127.0.0.1:8080/admin``).

In order to fully understand how the interface of the proposed application works, you can run it on example data.

Define the application with example data
----------------------------------------

.. code-block:: bash

    cp db.example.sqlite3 db.sqlite3


.. note::
    
    The website will now be composed of a set of example data.

You can log in to the administrator interface with the following credentials: 

.. code-block:: bash

    username: adminuser
    password: adminuser

Main concepts
=============

This is a main overview of the important components of the framework:

.. raw:: html
    :file: _static/documentation/overall.svg


Here is more detail for each of the principal components:

- **Experiment:** represents the architecture of the experiment with the associated pages (more details will be provided later), a JSON configuration of the experiment (path to data for example), a description and an availability status;
- **Session:** an experience can be attached to several sessions. Indeed, it can be wished that the experiment is available for different populations and/or that the stopping criterion of the experiment is different (time of the experiment). A JSON configuration is associated to a session and it also has an availability status (can also be active or not);
- **SessionProgress:** is one of the most important entities, it is at the heart of the application's operation. It allows the link between a session and a participant. When a participant wants to perform an experiment through a session, a new SessionProgress instance is created. This instance will manage the exchanges with the user, transmit the next stimulus to the user and define the stop of the experiment according to the stop criteria specified in the session. A SessionProgress, contains several SessionSteps, which store the user's response for each new stimulus transmitted.

With this insight, we will now go into more detail to understand how to create your own experience

Notion of template
=====================

First, we need to take a look at a very important concept of Django: the notion of ``template``. A **template** is an html page with a particular way of displaying data sent from the Django server. This is a common way in order to display data to the client in Django.

The following figure describe the process:

.. image:: _static/documentation/server_template.png
   :width: 60%
   :align: center


Here is an example of how Django works: 

.. code-block:: python
    
    def render_template_with_data(request):
        """
        Route available at `/experiment`
        Choose template and returns expected data
        """

        data = {
            "experiment": "My experiment title"
        }

        return render(request, "templates/experiment.html", data)


The template code example:

.. code-block:: html

    ...
    <!-- displays return data using key -->
    <h3>{{ experiment }}</h3>
    ...

.. note::

    Don't worry, you won't need to create Django queries, however, you will create templates if needed to specify the display you want.

Experiments
===========

The introduction to templates is important because we have mentioned in the main concepts that an experiment is composed of pages.


Page description
~~~~~~~~~~~~~~~~~


Indeed, an experiment is composed of 4 pages:

.. raw:: html
    :file: _static/documentation/pages.svg


- **The information page:** it may be necessary to ask some information from the participant, or to inform him about certain aspects of the experience. This is what the hint page allows;
- **The example page:** which provides instructions for a good understanding of the participating experience. It can be visible without going through the experience;
- **The main page:** this is where the experience will unfold, it will receive the new stimulus at each step, and will ask the participant to respond accordingly;
- **The end page:** when the SessionProgress instance determines the end of the participant's experience session, the end page is proposed to the participant.


Page creation
~~~~~~~~~~~~~

It is possible to create a particular page from the administrator interface (``/admin``). Each page requires a particular template and can be selected at creation. Each variable entered in the page configuration can be displayed in a particular template.


The folder ``experiments/templates/pages`` contains all the Django templates currently available for pages. Each sub-folder: ``end``, ``examples``, ``information``, ``main`` is associated with a particular type of page. This is how the *admin* interface provides you with only the possible templates.

.. warning::

    In order for an experiment to be created, it must be associated with each of the requested pages.

.. warning::

    For a new template to be taken into account in the administrator interface, the server must be restarted.


Associate styles and Javascript 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ToDo...


Base template of Page 
~~~~~~~~~~~~~~~~~~~~~

ToDo...

    
    
Session
===========

ToDo...

Session Progress
================

ToDo...