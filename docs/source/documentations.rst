======================================
A tour of Behavioral online experiment
======================================

Introduction
============

This documentation will allow you to get to know the framework and the administrator interface. It will detail the concepts and the idea behind the abstraction for the creation of online experiments.

.. note:: 
    It is highly recommended to read this documentation in parallel with the administrator interface (which is available at ``http://127.0.0.1:8080/admin``).


Here is a main overview of the important components of the framework:

.. raw:: html
    :file: _static/documentation/overall.svg

Template introduction
=====================

Before going into details, we need to take a look at a very important concept of Django: the notion of ``template``. A **template** is an html page with a particular way of displaying data sent from the Django server. This is common way we display data to the client in Django.

The following figure describe the process:

.. image:: _static/documentation/server_template.png
   :width: 70%
   :align: center

Here is an example of how Django works: 

.. code-block:: python
    
    def render_template_with_data(request):
        """
        Choose template and returns expected data
        """

        data = {
            "experiment": "My experiment title"
        }

        return render(request, "templates/example.html", data)


.. code-block:: html

    ...
    <!-- displays return data using key -->
    <h3>{{ experiment }}</h3>
    ...

.. note::

    Don't worry, you won't need to create Django queries, however, you will create templates if needed to specify the display you want.

Experiments
===========

The introduction to templates is important because we will explain their use in the design of an experiment.


Experiment representation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html
    :file: _static/documentation/experiment.svg



Experiment pages
~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html
    :file: _static/documentation/pages.svg