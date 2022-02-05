from email.policy import default
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.urls import reverse
from uuid import uuid4
from datetime import timedelta
import os

from .utils import create_choice_field

# some parameters
static_folder = 'static'
module_name = 'expe'
templates_path = os.path.join(module_name, 'templates')

# specific pages
example_template_path = os.path.join(templates_path, 'examples')
information_template_path = os.path.join(templates_path, 'information')
main_template_path = os.path.join(templates_path, 'main')
end_template_path = os.path.join(templates_path, 'end')

# styles and javascript
javascript_folder_path = os.path.join(static_folder, 'experiment', 'js')
css_folder_path = os.path.join(static_folder, 'experiment', 'css')

# All experiments django model
class Page(models.Model):
    """
    Generic Page model
    """
    javascript_files = []

    # get all javascript files
    for js in sorted(os.listdir(javascript_folder_path)):
        js_file_path = os.path.join(javascript_folder_path, js).replace(f'{static_folder}/', '')
        javascript_files.append((js_file_path, js_file_path))

    css_files = []

    # get all css files
    for css in sorted(os.listdir(css_folder_path)):
        css_file_path = os.path.join(css_folder_path, css).replace(f'{static_folder}/', '')
        css_files.append((css_file_path, css_file_path))

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=255)
    javascripts = MultiSelectField(choices=javascript_files, null=True, blank=True)
    styles = MultiSelectField(choices=css_files, null=True, blank=True)
    config = models.JSONField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    template = models.CharField(max_length=255, 
                                null=False)

    class Meta:
        abstract = True

class ExamplePage(Page):
    """
    Specific example page
    """
    template = create_choice_field(example_template_path)

class MainPage(Page):
    """
    Specific main page
    """
    template = create_choice_field(main_template_path)

class InformationPage(Page):
    """
    Specific main page
    """
    template = create_choice_field(information_template_path)

class EndPage(Page):
    """
    Specific main page
    """
    template = create_choice_field(end_template_path)


class Experiment(models.Model):

    """
    Based model of Experiment
    """
    # define experiment required field
    title = models.CharField(max_length=255)
    
    # page members definition
    example_page = models.ForeignKey(ExamplePage, on_delete=models.PROTECT, null=True, related_name='experiment')
    information_page = models.ForeignKey(InformationPage, on_delete=models.PROTECT, null=True, related_name='experiment')
    main_page = models.ForeignKey(MainPage, on_delete=models.PROTECT, null=True, related_name='experiment')
    end_page = models.ForeignKey(EndPage, on_delete=models.PROTECT, null=True, related_name='experiment')

    estimated_duration = models.DurationField(default=timedelta(minutes=0),
                        help_text='hh:mm:ss')
    
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
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT, related_name='sessions')
    is_active = models.IntegerField(default=1, blank=True, null=True, 
                                    help_text ='Session will be displayed but not accessible', 
                                    choices =((1, 'Active'), (0, 'Inactive')))
    is_available = models.IntegerField(default=1, blank=True, null=True, 
                                    help_text ='Session will not be displayed if disabled', 
                                    choices =((1, 'Available'), (0, 'Disabled')))
    created_on = models.DateTimeField(auto_now_add=True)


class UserExperiment(models.Model):
    """
    User model which can be attached to sessions of experiment
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    sessions = models.ManyToManyField(Session, null=True, related_name='users')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return self.name


class ExperimentProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    session = models.ForeignKey(Session, null=True, related_name='progress', on_delete=models.PROTECT)
    user = models.ForeignKey(UserExperiment, null=True, related_name='progress', on_delete=models.PROTECT)

    # progress data
    data = models.JSONField(null=True, blank=True)

class ExperimentStep(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    progress = models.ForeignKey(ExperimentProgress, null=False, related_name='steps', on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)

    # if necessary want to store binary data (such as python model)
    binary = models.BinaryField(null=True, blank=True)

    # data which should contain everything for experiment step
    data = models.JSONField(null=True, blank=True)
