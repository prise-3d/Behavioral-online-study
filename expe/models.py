from email.policy import default
from pyexpat import model
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.urls import reverse
from uuid import uuid4
from datetime import timedelta
import os
    
# Some parameters
example_template_path = os.path.join('expe', 'templates', 'examples')
javascript_folder_path = os.path.join('static', 'experiment', 'js')
css_folder_path = os.path.join('static', 'experiment', 'css')

# All experiments django model
class Page(models.Model):
    """
    Generic Page model
    """
    javascript_files = []

    # get all javascript files
    for js in sorted(os.listdir(javascript_folder_path)):
        _, filename = os.path.split(js)
        javascript_files.append((js, filename))

    css_files = []

    # get all css files
    for css in sorted(os.listdir(css_folder_path)):
        _, filename = os.path.split(css)
        css_files.append((css, filename))

    name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=255)
    javascripts = MultiSelectField(choices=javascript_files, null=True, blank=True)
    styles = MultiSelectField(choices=css_files, null=True, blank=True)
    config = models.JSONField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class ExamplePage(Page):
    """
    Specific example page
    """
    # TODO: make this field generic based on class name
    example_templates = []

    # get all expected templates
    for template in sorted(os.listdir(example_template_path)):
        _, filename = os.path.split(template)
        example_templates.append((template, filename))

    template = models.CharField(max_length=255, 
                                null=False,
                                help_text=f'You can add templates into: {example_template_path}',
                                choices=example_templates)

class Experiment(models.Model):

    """
    Based model of Experiment
    """
    # define experiment required field
    title = models.CharField(max_length=255)
    example_page = models.ForeignKey(ExamplePage, on_delete=models.PROTECT, null=True, related_name='experiment')
    estimated_duration = models.DurationField(default=timedelta(minutes=0),
                        help_text='hh:mm:ss')
    # TODO: add color box field
    # TODO: icon experiment field
    slug = models.SlugField(unique=True, max_length=255, blank=True,
                           help_text='This field is not required and will be generated automatically when the object is saved based on the title of the experiment')
    description = models.TextField()
    is_active = models.IntegerField(default=1, blank=True, null=True, 
                                    #help_text ='Active,0->Inactive', 
                                    choices =((1, 'Active'), (0, 'Inactive')))
    created_on = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('experiment', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(self.title)
        super(Experiment, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Session(models.Model):

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT, related_name='sessions')
    is_active = models.IntegerField(default=1, blank=True, null=True, 
                                    #help_text ='Active,0->Inactive', 
                                    choices =((1, 'Active'), (0, 'Inactive')))
    created_on = models.DateTimeField(auto_now_add=True)


class UserExperiment(models.Model):
    """
    User model which can be attached to sessions of experiment
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    sessions = models.ManyToManyField(Session, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return self.name


class ExperimentProgress(models.Model):
    pass