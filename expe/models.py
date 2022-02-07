from email.policy import default
from django.db import models
from polymorphic.models import PolymorphicModel

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.urls import reverse
from uuid import uuid4
from datetime import timedelta
import os
from django.conf import settings

from .utils import create_choice_field
from abc import abstractmethod


# some parameters
static_folder = settings.RELATIVE_STATIC_URL
module_name = 'expe'
pages_templates_path = os.path.join(module_name, 'templates', 'pages')

# specific pages
example_template_path = os.path.join(pages_templates_path, 'examples')
information_template_path = os.path.join(pages_templates_path, 'information')
main_template_path = os.path.join(pages_templates_path, 'main')
end_template_path = os.path.join(pages_templates_path, 'end')

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
        js_file_path = os.path.join(javascript_folder_path, js).replace(f'{static_folder}', '')
        javascript_files.append((js_file_path, js_file_path))

    css_files = []

    # get all css files
    for css in sorted(os.listdir(css_folder_path)):
        css_file_path = os.path.join(css_folder_path, css).replace(f'{static_folder}', '')
        css_files.append((css_file_path, css_file_path))

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=255)
    javascripts = MultiSelectField(choices=javascript_files, null=True, blank=True)
    styles = MultiSelectField(choices=css_files, null=True, blank=True)
    content = models.JSONField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
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
    id = models.AutoField(primary_key=True, editable=False, unique=True)
    title = models.CharField(max_length=255)
    
    # page members definition
    example_page = models.ForeignKey(ExamplePage, on_delete=models.PROTECT, null=True, related_name='experiment')
    information_page = models.ForeignKey(InformationPage, on_delete=models.PROTECT, null=True, related_name='experiment')
    main_page = models.ForeignKey(MainPage, on_delete=models.PROTECT, null=True, related_name='experiment')
    end_page = models.ForeignKey(EndPage, on_delete=models.PROTECT, null=True, related_name='experiment')

    slug = models.SlugField(unique=True, max_length=255, editable=False, blank=True,
                           help_text='This field is not required and will be generated automatically when the object is saved based on the title of the experiment')
    description = models.TextField()
    is_available = models.IntegerField(default=1, blank=True, null=True, 
                                    choices =((1, 'Available'), (0, 'Disabled')))
    created_on = models.DateTimeField(auto_now_add=True)

    config = models.JSONField(null=True, blank=True)

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

    id = models.AutoField(primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=255)
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT, related_name='sessions')

    # progresses = models.ManyToManyField(SessionProgress, editable=False, related_name='session')

    estimated_duration = models.DurationField(default=timedelta(minutes=0),
                help_text='hh:mm:ss')

    progress_choice = models.CharField(max_length=255, 
                            null=False,
                            help_text=f'You can add progress classes into: expe/experiments',
                            choices=[('default', 'default')]) # in order to override, need of pre-filled

    is_active = models.IntegerField(default=1, blank=True, null=True, 
                                    help_text ='Session will be displayed but not accessible', 
                                    choices =((1, 'Active'), (0, 'Inactive')))
    is_available = models.IntegerField(default=1, blank=True, null=True, 
                                    help_text ='Session will not be displayed if disabled', 
                                    choices =((1, 'Available'), (0, 'Disabled')))
    created_on = models.DateTimeField(auto_now_add=True)

    config = models.JSONField(null=True, blank=True)


class Participant(models.Model):
    """
    User model which can be attached to sessions of experiment
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    # progresses = models.ManyToManyField(SessionProgress, editable=False, related_name='participant')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return self.name

class SessionProgress(PolymorphicModel):
    """
    Store the progress of a session for an ExperimentUser
    """

    id = models.AutoField(primary_key=True, editable=False, unique=True)
    session = models.ForeignKey(Session, null=True, related_name='progresses', on_delete=models.PROTECT)
    participant = models.ForeignKey(Participant, null=True, related_name='progresses', on_delete=models.PROTECT)
    is_started = models.BooleanField(default=False, editable=False, null=False)
    is_finished = models.BooleanField(default=False, editable=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True)

    # progress data
    data = models.JSONField(null=True, blank=True)

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


class SessionStep(models.Model):
    """
    Define a step of an SessionProgress of an Participant during a Session
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)

    # generic way to add specific SessionProgress object
    progress_type = models.ForeignKey(ContentType, related_name='steps', on_delete=models.PROTECT)
    progress_id = models.PositiveIntegerField()
    progress = GenericForeignKey('progress_type', 'progress_id')

    # if necessary want to store binary data (such as python model)
    binary = models.BinaryField(null=True, blank=True)

    # data for an experiment step
    data = models.JSONField(null=True, blank=True)
