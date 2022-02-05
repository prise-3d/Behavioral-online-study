from django.contrib import admin
from django.contrib import messages
from django.db import models
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Experiment, UserExperiment, ExperimentSession, ExperimentProgress
from .models import ExamplePage, InformationPage, MainPage, EndPage
from .experiments.classical import ClassicalExperimentProgress


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        
        # Add some logic here to base your choices on.
        if db_field.name == 'progress_choice':
            cl_choices = []
            for cl in ExperimentProgress.__subclasses__():
                full_name = '.'.join([cl.__module__, cl.__name__])
                cl_choices.append((full_name, full_name))
            
            db_field.choices = cl_choices

        return super(ExperimentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    list_display = ('title', 'active', 'created_on')

    def active(self, obj):
        return obj.is_active == 1
    active.boolean = True

    actions = ['make_active', 'make_inactive']

    @admin.action(description='Marked as active')
    def make_active(self, request, queryset):
        queryset.update(is_active = 1)
        messages.success(request, "Selected experiment(s) Marked as active Successfully!")

    @admin.action(description='Marked as inactive')
    def make_inactive(modeladmin, request, queryset):
        queryset.update(is_active = 0)
        messages.success(request, "Selected experiment(s) Marked as Inactive Successfully!")

    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ExperimentSession)
class ExperimentSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'active', 'available', 'created_on')

    def active(self, obj):
        return obj.is_active == 1
    active.boolean = True

    def available(self, obj):
        return obj.is_available == 1
    available.boolean = True

    actions = ['make_active', 'make_inactive', 'make_disabled', 'make_available']

    @admin.action(description='Marked as active')
    def make_active(self, request, queryset):
        queryset.update(is_active = 1)
        messages.success(request, "Selected session(s) Marked as active Successfully!")

    @admin.action(description='Marked as inactive')
    def make_inactive(modeladmin, request, queryset):
        queryset.update(is_active = 0)
        messages.success(request, "Selected session(s) Marked as Inactive Successfully!")
 
    @admin.action(description='Marked as disabled')
    def make_disabled(self, request, queryset):
        queryset.update(is_available = 0)
        messages.success(request, "Selected session(s) Marked as disabled Successfully!")

    @admin.action(description='Marked as available')
    def make_available(modeladmin, request, queryset):
        queryset.update(is_available = 1)
        messages.success(request, "Selected session(s) Marked as available Successfully!")

    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }
 
@admin.register(UserExperiment)
class UserExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on')


@admin.register(ExamplePage, InformationPage, MainPage, EndPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_on')

    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(ClassicalExperimentProgress)
class ClassicalExperimentProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_on')
