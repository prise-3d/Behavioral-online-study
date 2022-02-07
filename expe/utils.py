# main imports
import os
from django.db import models
from importlib import import_module

# some parameters
static_folder = 'static'
module_name = 'expe'
templates_path = os.path.join(module_name, 'templates')

import importlib
import pkgutil

def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

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

def load_progress_class(module_path):

    # retrieve module and expected class
    modules = module_path.split('.')
    module_name = '.'.join(modules[:-1])
    class_name = modules[-1]

    # load module and get class
    module = import_module(module_name)
    progress_class = getattr(module, class_name)

    return progress_class