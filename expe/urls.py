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
    path('experiments/<slug:slug>/session/<int:session_id>', views.load_information_page, name='load_information'),
    path('experiments/<slug:slug>/start/<int:progress_id>', views.load_example_page, name='load_example'),
    path('experiments/<slug:slug>/run/<int:progress_id>', views.run_experiment_step, name='run_session'),
    path('experiments/experiment/stat', views.experiment_stat, name='experiment_stat'),
    path('user/checkuser', views.check_user, name='check_user'),

    # admin urlpatterns
    path('experiments/<slug:slug>/session/<int:session_id>/download', views.download_session_progresses, name='download_session'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)