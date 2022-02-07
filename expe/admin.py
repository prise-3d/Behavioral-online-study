from django.contrib import admin
from django.contrib import messages
from django.db import models
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Experiment, Participant, Session, SessionProgress
from .models import ExamplePage, InformationPage, MainPage, EndPage
from .experiments.classical import ClassicalSessionProgress


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'available', 'created_on')

    def available(self, obj):
        return obj.is_available == 1
    available.boolean = True

    actions = ['make_available', 'make_disabled']

    @admin.action(description='Marked as available')
    def make_active(self, request, queryset):
        queryset.update(is_available = 1)
        messages.success(request, "Selected experiment(s) Marked as available Successfully!")

    @admin.action(description='Marked as disabled')
    def make_inactive(modeladmin, request, queryset):
        queryset.update(is_available = 0)
        messages.success(request, "Selected experiment(s) Marked as disabled Successfully!")

    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'active', 'available', 'created_on')

    def formfield_for_dbfield(self, db_field, **kwargs):
        
        # recursively get all subclasses
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)])

        # Add some logic here to base your choices on.
        if db_field.name == 'progress_choice':
            cl_choices = []
            for cl in all_subclasses(SessionProgress):
                full_name = '.'.join([cl.__module__, cl.__name__])
                cl_choices.append((full_name, full_name))
            
            db_field.choices = cl_choices

        return super(SessionAdmin, self).formfield_for_dbfield(db_field, **kwargs)

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
 
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on')


@admin.register(ExamplePage, InformationPage, MainPage, EndPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_on')

    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(ClassicalSessionProgress)
class ClassicalSessionProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant', 'created_on')
