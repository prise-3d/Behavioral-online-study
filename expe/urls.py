from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'expe'

urlpatterns = [
    path('', views.index, name='index'),
    path('experiments', views.experiments, name='experiments'),
    path('experiments/<slug:name>', views.experiment, name='experiment')
    # path('expe', views.expe, name='expe'),
    # path('expe_end', views.expe_end, name='expe_end'),
    # path('presentation', views.presentation, name='presentation'),
    # path('update_session_user', views.update_session_user, name='update_session_user'),
    # path('admin/results', views.list_results, name='results'),
    # path('admin/results/<str:expe>', views.list_results, name='results_expe'),
    # path('admin/download', views.download_result, name='download')
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)