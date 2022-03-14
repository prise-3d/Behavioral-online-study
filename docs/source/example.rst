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

We start on the web administrator interface: ``http://127.0.0.1:8000/admin/experiments/``

.. image:: _static/documentation/admin_interface.png
   :width: 80%
   :align: center


1.1. Information Page
~~~~~~~~~~~~~~~~~~~~~

We will start by creating the page for entering information to the user. To do this:
   
- in the Django Administration interface, use the ``+Add`` of information;

- fill in the different fields of your page, like the name "Ponzon Illusion" and the title "ponzon_illusion". The name identifies the page in the administrator interface, the title will be used in the URL;

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


1.2. Example page
~~~~~~~~~~~~~~~~~

In the admin interface use ``+Add`` for examples pages, we find the same information to fill in:

- the name field to "Ponzo Example";
- the title field to "ponzo_example"; 
- the field Javascript: none selected;
- the field styles selecting: ``hide_footer.css`` and ``hide_sidebar.css``;
- the template field: ``experiments/templates/pages/examples/one_image.html``.

The JSON content field is composed of:

.. code:: json

    {
      "question": "Are the two segment equals?",
      "description": "Press the LEFT button if you think the segment are equals, or the RIGHT button if you think they are differents.",
      "answer": "The correct answer is yes!",
      "image": {
        "src": "resources/images/ponzo/ponzo10.png",
        "width": 500,
        "height": 500
      }
    }

At the end click on ``SAVE``.

1.3. Main Page
~~~~~~~~~~~~~~

In the admin interface use ``+Add`` for mains pages, we find the same information to fill in:

- the name field to "Ponzo Main";
- the title field to "ponzo_main"; 
- the field Javascript: ``js/binary_buttons_answer.js``;
- the field styles selecting: ``hide_footer.css`` and ``hide_sidebar.css``;
- the template field: ``experiments/templates/pages/main/one_image_buttons.html``.

The JSON field to:

.. code:: json

    {
      "question": "Are the two segment equals?",
      "description": "Press the LEFT button if you think the segment are equals, or the RIGHT button if you think they are differents."
    }


.. note::

    An image will be loaded in the main page, but we will see later that its loading is dynamic.


1.4. End Page
~~~~~~~~~~~~~

In the admin interface use ``+Add`` for mains pages, we find the same information to fill in:

- the name field to "Ponzo End";
- the title field to "ponzo_end"; 
- the field Javascript: ``toggle_sidebar.js``;
- the field styles selecting: none selected;
- the template field: ``experiments/templates/pages/end/basic_end.html``.

And the JSON field to:

.. code:: json

    {
      "end_text": "The experiment is now finished.",
      "thanks_text": "Thanks for your participation!"
    }


Then click on ``SAVE`` button.

1.5. Experiment creation
~~~~~~~~~~~~~~~~~~~~~~~~

In the admin interface use ``+Add`` for experiments, you can fill in the different fields as below:

- the title field to "Ponzo experiment";
- the name field to "Ponzo experiment";
- for each page field, select the new associated created page;
- add the following description of the experiment:


.. code:: text

    Ponzo experiment proposes an image and ask if the segment are equals or not inside this image

- set it as available;
- let the JSON config as empty;

Then click on ``SAVE`` in order to create the experiment.


2. Create a Session Progress class
==================================

As a reminder, a SessionProgress is composed of 4 main methods as detailed below:

.. code:: python

    class SessionProgress():

        @abstractmethod
        def start(self, participant_data):
            """
            Define and init some progress variables
            """
            pass

        @abstractmethod
        def next(self, step, answer) -> dict:
            """
            Define next step data object taking into account current step and answer

            Return: JSON data object
            """
            pass

        @abstractmethod
        def progress(self) -> float:
            """
            Define the percent progress of the experiment

            Return: float progress between [0, 100]
            """
            pass

        @abstractmethod
        def end(self) -> bool:
            """
            Check whether it's the end or not of the experiment

            Return: bool
            """
            pass


The figure below details where the methods of the SessionProgress instance are realized:

.. image:: _static/documentation/global_scheme.png
   :width: 95%
   :align: center


In the ``experiments/experiments`` folder of the projet create a ``ponzo.py`` python file.


.. code:: python

    from ..models import SessionProgress

    class PonzoSessionProgress(SessionProgress):
        pass

2.1. The start method
~~~~~~~~~~~~~~~~~~~~~

The start method should be composed of:

.. code::

    def start(self, participant_data):

        # need to be initialized in order to start experiment
        if self.data is None:
            self.data = {}

        self.data['iteration'] = 0
        self.data['participant'] = {
            'know-cg': participant_data['basic-info-know-cg'],
            'why': participant_data['basic-info-why'],
            'glasses': participant_data['basic-info-glasses'],
        }

        # always save state
        self.save()

3. Create a new Session
=======================