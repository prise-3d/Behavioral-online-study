from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'expe'

urlpatterns = [
    path('', views.index, name='index'),
    path('experiments', views.experiments, name='experiments'),
    path('experiments/<slug:slug>', views.experiment, name='experiment'),
    path('experiments/<slug:slug>/example/<int:id>', views.preview_example_page, name='example'),
    path('experiments/<slug:expe_slug>/session/<int:session_id>', views.load_information_page, name='load_information'),
    path('user/checkuser', views.check_user, name='check_user'),
    path('user/checkprogress', views.check_progress, name='check_progress'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)