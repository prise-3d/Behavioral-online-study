=====================================
Advanced usages
=====================================


Custom styles and javascript for template
=========================================

It is possible to define specific code of styles or javascript within a page template. For this purpose, you must specify the necessary code in the appropriate block:

.. code:: html

    <!-- Custom styles -->
    {% block custom_stylesheets %}
        <style type="text/css" media="screen">

            /* Add style rules here */

        </style>
    {% endblock %}

    {% block content %}
        <!-- Specific content of the block -->
    {% endblock %}

    <!-- Custom javascript -->
    {% block custom_javascripts %}
        <script type="text/javascript">
            console.log('Hello world');
        </script>
    {% endblock %}

This can be notably useful when the javascript code or styles are short and specific to the page. Otherwise, it is preferable to use the classic scripts available for all pages.


Dynamic media content in Session Progress
=========================================

ToDo...

Store binary data into SessionProgress
======================================


If you are using specific templates for your development, you should know that the SessionProgress template has a binary storage field called ``binary``.

This makes it possible to save and reload binary python objects using the pickle tool:


.. code:: python

    import pickle


    def next(self, step, answer) -> dict:

        # example python object
        myObj = {
            "type": "binary"
            "answer": 42
        }

        # store binary object data
        myObj_bytes = pickle.dumps(myObj)
        self.binary = myObj_bytes

        # save the current SessionProgress instance
        self.save()

        # load current object instance
        obj = pickle.loads(self.binary)


Prepare server for production mode
==================================
