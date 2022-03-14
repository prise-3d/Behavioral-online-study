Description
=====================================

.. image:: _static/dial_logo.png
   :width: 50 px
   :align: center
   
Context
-------

This project is a framework for designing behavioral online experiment. It proposes a common base for all experiments using the Django Python web framework. The use of Python allows to easily integrate libraries on the application server that can be used for the experiment.


Motivation
----------

The development of experiments for the collection of information and measures from participants on human behavior have been increasingly implemented on web platforms. The recent health crisis and the diversity of the population that can be affected are two main reasons for this trend.

However, setting up such a platform is not necessarily easy, because it requires skills to create such a website. This framework aims to propose a generic approach to online experiment design in order to simplify this task for those wishing to create one.

The proposed framework is based on the Django Python framework, which allows the integration of python code for experiment management in backend. Moreover, it proposes a certain way to approach an experiment, making it as generic as possible:


Target Audience
---------------

This framework is intended for anyone who wants to quickly implement an online experiment without having any web skills. The framework tries to simplify the client/server interactions as much as possible, however, there are still elements to be specified by the experiment builder, such as how to display the information and how the information is to be retrieved from the client, but still in a very accessible way.