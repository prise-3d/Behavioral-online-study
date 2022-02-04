# django imports
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseNotAllowed
from django.conf import settings
from .models import Experiment

def index(request):
    """Default home page

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new page to render with website explanation
    """
    
    return render(request, 'expe/index.html')


def experiments(request):
    """Page with experiment list

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new page to render with experiments data
    """

    # retrieve each experiment
    experiments = Experiment.objects.all().exclude(is_active=0, sessions__is_active=0).order_by('-created_on')
    
    # experiments.all().sessions = experiments.all().sessions.all().exclude(is_active=0) 
    context = {
        'experiments': experiments,
    }

    return render(request, 'expe/experiments.html', context)

def experiment(request, slug):
    """Detail of experiment with example page

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new page to render with experiment detail data
    """

    # access using unique slug
    experiment = Experiment.objects.get(slug=slug)

    context = {
        'experiment': experiment,
    }

    return render(request, 'expe/experiment.html', context)
