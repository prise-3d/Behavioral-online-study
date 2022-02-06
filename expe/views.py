# django imports
from uuid import uuid4, UUID
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.core.serializers import serialize
from django.conf import Settings
from . import utils

from .models import ExamplePage, Experiment, ExperimentProgress, ExperimentSession, ExperimentStep, UserExperiment

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


def load_information_page(request, slug, session_id):
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
        session = ExperimentSession.objects.get(id=session_id)
        experiment = Experiment.objects.get(slug=slug)
        information_page = experiment.information_page
        progress = None

        progress_class = utils.load_progress_class(experiment.progress_choice)

        progress = None
        session_id_str = str(session_id) # avoid dict key issue...

        
        # check if necessary to reload progress
        if 'progress' in request.session:
            
            # check if session already started by user
            if session_id_str in request.session['progress']:

                try:
                    progress_id = int(request.session['progress'][session_id_str])
            
                    progress = progress_class.objects.get(id=progress_id)
                    
                    # enable to start new experiment session only if previous session progress is finished
                    # or with other criterion...
                    print('Check if session experiment is finished')
                    print(progress.is_finished)
                    if progress.is_finished == True:
                        progress = None
                    else:  # progress.is_started: # TODO: check if ok
                        context = {
                            'page': experiment.example_page,
                            'experiment': experiment, 
                            'progress': progress
                        }
                        
                        # dynamic rendering with use of custom page template
                        return render(request, f'{experiment.example_page.template}', context)

                except ValueError:
                    print(f'Error while attempted to retrieve progress')

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
            request.session['progress'][session_id_str] = progress.id
        
        # dynamic rendering with use of custom page template
        return render(request, f'{information_page.template}', context)

    else:
        return HttpResponse({
                'status_code': 404,
                'error': 'Error when generating information page'
            })


def load_example_page(request, slug, progress_id):
    """Enable to load the information page before starting experiment
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':

        # access using unique slug
        experiment = Experiment.objects.get(slug=slug)
        example_page = experiment.example_page

        progress_class = utils.load_progress_class(experiment.progress_choice)
        
        progress = progress_class.objects.get(id=progress_id)

        # TODO: get all data fields

        context = {
            'page': example_page,
            'experiment': experiment, 
            'progress': progress
        }
        
        # dynamic rendering with use of custom page template
        return render(request, f'{example_page.template}', context)

    else:
        return HttpResponse({
                'status_code': 404,
                'error': 'Error when generating information page'
            })


def run_experiment_step(request, slug, progress_id):
    """Enable to process an experiment for the current user progress 
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':
        # access using unique slug
        experiment = Experiment.objects.get(slug=slug)
        main_page = experiment.main_page

        progress_class = utils.load_progress_class(experiment.progress_choice)
        
        progress = progress_class.objects.get(id=progress_id)

        # process an experiment step
        if not progress.is_started:
            progress.start()
            progress.is_started = True
            progress.save()

        # TODO: get expected answer
        previous_step = None
        answer = 1 
        step_data = progress.next(previous_step, answer)

        # create new state
        experiment_step = ExperimentStep.objects.create(
            progress=progress,
            data=step_data
        )

        session = ExperimentSession.objects.get(id=progress.session.id)
        print(session.users.all())
        print('There is some expe steps:', ExperimentStep.objects.filter(progress_id=progress.id).all().count())

        if progress.end():
            
            # passed as finished state
            progress.is_finished = True
            progress.save()
            
            end_page = experiment.end_page

            context = {
                'page': end_page,
                'experiment': experiment, 
                'progress': progress
            }

            return render(request, f'{end_page.template}', context)

        context = {
            'page': main_page,
            'experiment': experiment, 
            'progress': progress,
            'progress_info': int(progress.progress()),
            'step': experiment_step
        }
        
        # dynamic rendering with use of custom page template
        return render(request, f'{main_page.template}', context)
    else:
        return HttpResponse({
                'status_code': 404,
                'error': 'Error when generating information page'
            })