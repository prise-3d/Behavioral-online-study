# django imports
from uuid import uuid4, UUID
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.core.serializers import serialize
from django.conf import Settings
from . import utils

from .models import ExamplePage, Experiment, ExperimentProgress, ExperimentSession, UserExperiment

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


def preview_example_page(request, slug, id):
    """Display example page of experiment

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new page to render with experiment example page
    """

    # access example page using unique slug
    example_page = ExamplePage.objects.get(id=id)
    experiment = Experiment.objects.get(slug=slug)

    # print(experiment.title)
    context = {
        'page': example_page,
        'experiment': experiment
    }

    # dynamic rendering with use of custom page template
    return render(request, f'{example_page.template}', context)


def check_user(request):
    """Check and add user if not exist
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])
    
    if 'user_uuid' in request.session:
        try:
            user = UserExperiment.objects.get(id=request.session['user_uuid'])
        except:
            user = None

    else:
        if 'user_uuid' not in request.POST:
            return JsonResponse({
                'status_code': 404,
                'error': 'Error when generating user'
            })

        user_uuid = request.POST.get('user_uuid')

        try:
            generated_uuid = UUID(user_uuid, version=4)
            
            # check if user exists in database
            user = UserExperiment.objects.get(id=generated_uuid)
            print(f'[{user.id}]: {user.name} access page')

        except ValueError:
            # If it's a value error, then the string 
            # is not a valid hex code for a UUID.
            user = None

    if user is None:

        # create new user if necessary
        user = UserExperiment.objects.create(
            name='Anonymous', 
        )
    # store or refresh if necessary the user id
    request.session['user_uuid'] = str(user.id)

    # return the created user instance
    data = serialize("json", [ user,  ], fields=('id', 'name', 'created_on'))

    return HttpResponse(data, content_type="application/json")


def load_information_page(request, expe_slug, session_id):
    """Enable to load the information page before starting experiment
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':
        
        try:
            user_uuid = request.session['user_uuid']
            generated_uuid = UUID(user_uuid, version=4)
            
            # check if user exists in database
            user = UserExperiment.objects.get(id=generated_uuid)

        except ValueError:
            # If it's a value error, then the string 
            # is not a valid hex code for a UUID.
            user = None
        
        if user is None:
            return HttpResponse({
                'status_code': 404,
                'error': 'Error when generating information page'
            })

        # access using unique slug
        experiment = Experiment.objects.get(slug=expe_slug)
        information_page = experiment.information_page
        session = ExperimentSession.objects.get(id=session_id)

        progress_class = utils.load_progress_class(experiment.progress_choice)
        
        progress = None
        session_id_str = str(session_id) # avoid dict key issue...

        # check if necessary to reload progress
        if 'progress' in request.session:
            
            # check if session already started by user
            if session_id_str in request.session['progress']:

                try:
                    progress_uuid = request.session['progress'][session_id_str]

                    print(f'Found user session progress for: (expe: {experiment.title}, progress: {progress_class.__name__}, session: {session.name})')

                    generated_uuid = UUID(progress_uuid, version=4)
                    progress = progress_class.objects.get(id=generated_uuid)

                    # enable to start new experiment session only if previous session progress is finished
                    if progress.is_finished:
                        progress = None
                    else:
                        # TODO: redirect to previous one
                        pass

                except ValueError:
                    return HttpResponse({
                        'status_code': 404,
                        'error': 'Error when generating information page'
                    })

        if progress is None:
            # create experiment progress dynamically
            progress = progress_class.objects.create(
                session=session,
                user=user
            )

        context = {
            'page': information_page,
            'experiment': experiment, 
            'progress': progress
        }

        if 'progress' not in request.session:
            request.session['progress'] = {}

        if session_id_str not in request.session['progress']:
            request.session['progress'][session_id] = str(progress.id)

        # dynamic rendering with use of custom page template
        return render(request, f'{information_page.template}', context)

    else:
        return HttpResponse({
                'status_code': 404,
                'error': 'Error when generating information page'
            })


def load_example_page(request, expe_slug, progress):
    """Enable to load the information page before starting experiment
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':
        # access using unique slug
        experiment = Experiment.objects.get(slug=expe_slug)
        information_page = experiment.information_page
        session = ExperimentSession.objects.get(id=session_id)

        # print(experiment.title)
        context = {
            'page': information_page,
            'experiment': experiment, 
            'session': session
        }
        
        # dynamic rendering with use of custom page template
        return render(request, f'{information_page.template}', context)