# main imports
import os
from django.db import models

# some parameters
static_folder = 'static'
module_name = 'expe'
templates_path = os.path.join(module_name, 'templates')

def create_choice_field(template_path):
    templates_files = []

    # get all expected templates
    for template in sorted(os.listdir(template_path)):
        template_path = os.path.join(template_path, template).replace(f'{templates_path}/', '')
        templates_files.append((template_path, template_path))

    template = models.CharField(max_length=255, 
                                null=False,
                                help_text=f'You can add templates into: {template_path}',
                                choices=templates_files)

    return template
        