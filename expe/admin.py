from django.contrib import admin
from django.contrib import messages

from .models import Experiment, UserExperiment, Session, ExamplePage

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
 


class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'active', 'created_on')

    def active(self, obj):
        return obj.is_active == 1
    active.boolean = True

    actions = ['make_active', 'make_inactive']

    @admin.action(description='Marked as active')
    def make_active(self, request, queryset):
        queryset.update(is_active = 1)
        messages.success(request, "Selected session(s) Marked as active Successfully!")

    @admin.action(description='Marked as inactive')
    def make_inactive(modeladmin, request, queryset):
        queryset.update(is_active = 0)
        messages.success(request, "Selected session(s) Marked as Inactive Successfully!")
 
    # def make_active(modeladmin, request, queryset):
    #     queryset.update(is_active = 1)
    #     messages.success(request, "Selected Record(s) Marked as Active Successfully !!")
  
    # def make_inactive(modeladmin, request, queryset):
    #     queryset.update(is_active = 0)
    #     messages.success(request, "Selected Record(s) Marked as Inactive Successfully !!")



class UserExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on')


class ExamplePageAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_on')


admin.site.register(ExamplePage, ExamplePageAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(UserExperiment, UserExperimentAdmin)