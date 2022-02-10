"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf.urls import handler404, handler500, handler403, handler400

handler404 = 'experiments.views.error_404'
handler500 = 'experiments.views.error_500'
handler403 = 'experiments.views.error_403'
handler400 = 'experiments.views.error_400'

urlpatterns = [
    path('', include('experiments.urls', namespace='experiments')),
    path('admin/', admin.site.urls),
]
