from django.contrib import admin
from django.contrib import messages
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from .models import Experiment, UserExperiment, Session
from .models import ExamplePage, InformationPage, MainPage, EndPage

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
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
 
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
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