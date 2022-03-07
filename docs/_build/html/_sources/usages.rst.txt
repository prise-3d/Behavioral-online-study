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

Il est possible d'exploiter des images disponibles depuis le dossier `static` comme stimuli. Parfois, il peut être nécessaire de générer une nouvelle image, soit par la fusion de deux autres ou avec d'autres particularités. 

Il est important que ces images soit également accessibles lors de la génération. Il faut donc qu'elle soit sauvegardées dans le dossier de ressources externes relatif : ``settings.RELATIVE_STATIC_URL``.

Voici un exemple de génération de nouvelle image:

.. code:: python

    from django.conf import settings
    from PIL import Image
    import numpy as np

    ...

    def next(self, step, answer) -> dict:

        cornel_box_path = 'resources/images/cornel_box'
        
        # need to take care of static media folder
        images_path = sorted([ 
                    os.path.join(cornel_box_path, img) 
                    for img in os.listdir(os.path.join(settings.RELATIVE_STATIC_URL, cornel_box_path)) 
                ])


        # access of two random images
        first_image_path = os.path.join(settings.RELATIVE_STATIC_URL, random.choice(images_path))
        second_image_path = os.path.join(settings.RELATIVE_STATIC_URL, random.choice(images_path))

        first_image_arr = np.array(Image.open(first_image_path))
        second_image_arr = np.array(Image.open(second_image_path))

        final = np.concatenate([first_image_arr, second_image_arr], axis=1)

        # save generated image into static folder (need the access of the new image)
        generated_path = os.path.join(settings.RELATIVE_STATIC_URL, 'generated')

        if not os.path.exists(generated_path):
            os.makedirs(generated_path)

        # save the image
        output_img_path = os.path.join(generated_path, 'tmp.png')
        Image.fromarray(final).save(output_img_path)

Store binary data into SessionProgress
======================================


If you are using specific templates for your development, you should know that the SessionProgress template has a binary storage field called ``binary``.

This makes it possible to save and reload binary python objects using the pickle tool:


.. code:: python

    import pickle

    ...

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


First your need to make sure the whole installation have been done:

.. code:: bash

    python manage.py makemigrations
    python manage.pu migrate
    bash create_admin.sh


In the ``webapp/settings.py``, set:

- STATIC_ROOT which must point to the folder allowing access to resources from outside (apache2 or Nginx server). Example: ``/var/www/html/static``.


Collect all the static file into a folder allowing access to resources from outside (apache2 or Nginx server):

.. code:: python

    python manage.py collectstatic


Then, in the ``webapp/settings.py``, you need to update:

- STATIC_URL with your expected domain name (https//yourdomain.com)
- DEBUG = False
- ALLOWED_HOSTS array with your domain name
- RELATIVE_STATIC_URL which must point to the folder allowing access to resources from outside (apache2 or Nginx server). Example: ``../../www/html/static``.


.. note:: warning

    Each time a new style file, a javascript file, a new instance of SessionProgress and any type of external resource is added to the ``static`` folder, it is necessary to update and restart the server in production.