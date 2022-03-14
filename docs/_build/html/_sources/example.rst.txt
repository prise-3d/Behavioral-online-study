=================================
Create an experiment from scratch
=================================

1. Create an experiment entity
==============================

An experiment is composed of 4 pages : information, example, main and end. The administrator interface allows you to create each page, but it will be necessary for each page to associate Django template and CSS and Javascript styles. 

Here are the different creation steps:

- Create the 4 pages of the experiment: information, example, main and end.
- modify for each page (if necessary) an associated template : experiments/templates/pages
- Once a template is defined: create for each page, its entity in the admin interface with the desired template.
- Then, create the experiment from the 4 pages.

For this, for the edition of the code, it is recommended to open the behavioral-online-experiment folder in folder mode (for example with Visual Studio Code or another code editor).

We start on the web administrator interface: ``http://127.0.0.1:8000/admin/experiments/``.

1.1 Information Page
~~~~~~~~~~~~~~~~~~~~

We will start by creating the page for entering information to the user. To do this:
   
- in the Django Administration interface, use the "+Add" of information;

- fill in the different fields of your page, like the name (Ponzon Illusion" and the title (ponzon_illusion). The name identifies the page in the administrator interface, the title will be used in the URL;

- Then you have to select the javascripts and styles files. For this example, we select only ``toggle_sidebar.js`` (the styles and javascript files are available in the project in the folder: ``static/experiment``, but it is not necessary to modify them right away);

- A selection field allows to choose the template of our choice. By default, there is only one: ``basic_information.html``, available in the ``experiments/templates/pages/information`` folder; 

- A JSON field is also available, it allows to specify the content that will be available in the Django template. For this page, it will only contain a sentence inviting the user to enter a data form:

.. code:: json   

    {
      "question": "Please fill the form below:"
    }


It is in this HTML template that the JSON field information will be displayed (this one uses only the question field):

.. code:: html

        ...
        <!-- Page Heading -->
        <div class="text-center">
            <h5>{{page.content|from_json:"question"}}</h5>
        </div>
        ...

If you create your own templates, you can declare JSON fields that can be processed in the template.

At the end click on ``SAVE``.


1.2 Example page
~~~~~~~~~~~~~~~~
