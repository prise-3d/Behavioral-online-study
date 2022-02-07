# django imports
import os
from uuid import uuid4, UUID
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.http import Http404
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.core.serializers import serialize
from . import utils
from django.contrib.auth.decorators import user_passes_test
import json

from .models import ExamplePage, Experiment, Session, SessionStep, Participant

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
    experiments = Experiment.objects.all().exclude(is_available=0, sessions__is_active=0).order_by('-created_on')
    
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
        'progress_session': request.session['progress'] if 'progress' in request.session else None,
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


def check_participant(request):
    """Check and add participant if not exist
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])
    
    if 'participant_uuid' in request.session:
        try:
            participant = Participant.objects.get(id=request.session['participant_uuid'])
        except:
            participant = None

    else:
        if 'participant_uuid' not in request.POST:
            context = {
                'error_code': 404,
                'message': 'Page request not found'
            }
            return render(request, 'expe/error.html', context)
        

        participant_uuid = request.POST.get('participant_uuid')

        try:
            generated_uuid = UUID(participant_uuid, version=4)
            
            # check if participant exists in database
            participant = Participant.objects.get(id=generated_uuid)
            print(f'[{participant.id}]: {participant.name} access page')

        except ValueError:
            # If it's a value error, then the string 
            # is not a valid hex code for a UUID.
            participant = None

    if participant is None:

        # create new participant if necessary
        participant = Participant.objects.create(
            name='Anonymous', 
        )
    # store or refresh if necessary the participant id
    request.session['participant_uuid'] = str(participant.id)

    # return the created participant instance
    data = serialize("json", [ participant,  ], fields=('id', 'name', 'created_on'))

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
            participant_uuid = request.session['participant_uuid']
            generated_uuid = UUID(participant_uuid, version=4)
            
            # check if participant exists in database
            participant = Participant.objects.get(id=generated_uuid)

        except ValueError:
            # If it's a value error, then the string 
            # is not a valid hex code for a UUID.
            participant = None
        
        if participant is None:
            context = {
                'error_code': 404,
                'message': 'Page request not found'
            }
            return render(request, 'expe/error.html', context)
        

        # access using unique slug
        session = Session.objects.get(id=session_id)

        if not session.is_available:
            context = {
                'error_code': 404,
                'message': 'Page request not found'
            }
            return render(request, 'expe/error.html', context)

        experiment = Experiment.objects.get(slug=slug)
        information_page = experiment.information_page
        progress = None

        progress_class = utils.load_progress_class(session.progress_choice)

        current_progress = None
        session_id_str = str(session_id) # avoid dict key issue...
        
        # check if necessary to reload progress
        if 'progress' in request.session:
            
            # check if session already started by participant
            if session_id_str in request.session['progress']:

                try:
                    progress_id = int(request.session['progress'][session_id_str])
            
                    progress = progress_class.objects.get(id=progress_id)
                    
                    if progress.data is None:
                        
                        context = {
                            'page': experiment.information_page,
                            'experiment': experiment, 
                            'progress': progress,
                            'session': session
                        }

                        # if not start then redirect to information page
                        return render(request, f'{experiment.information_page.template}', context)

                    # enable to start new experiment session only if previous session progress is finished
                    # or with other criterion...
                    if progress.is_finished == True:
                        # remove from session previous one
                        current_progress = None
                        del request.session['progress'][session_id_str]
            
                    else:  
                        
                        # start if experiment is started or not (participant quit at example or not)
                        try:
                            previous_step = SessionStep.objects.filter(progress_id=progress.id).latest('created_on')

                            context = {
                                'page': experiment.main_page,
                                'experiment': experiment,
                                'progress': progress,
                                'session': session,
                                'progress_info': int(progress.progress()),
                                'step': previous_step
                            }
                            
                            # dynamic rendering with use of custom page template
                            return render(request, f'{experiment.main_page.template}', context)
                        except:
                            print(f'Cannot load with previous step')

                            context = {
                                'page': experiment.example_page,
                                'experiment': experiment, 
                                'session': session,
                                'progress': progress
                            }
                            
                            # dynamic rendering with use of custom page template
                            return render(request, f'{experiment.example_page.template}', context)

                        

                except ValueError or progress_class.DoesNotExist:
                    print(f'Error while attempted to retrieve progress')

        if current_progress is None:
            # create experiment progress dynamically
            current_progress = progress_class.objects.create(
                session=session,
                participant=participant
            )

        context = {
            'page': information_page,
            'experiment': experiment, 
            'progress': current_progress,
            'session': session,
        }

        if 'progress' not in request.session:
            request.session['progress'] = {}

        if session_id_str not in request.session['progress']:
            request.session['progress'][session_id_str] = current_progress.id
        
        # dynamic rendering with use of custom page template
        return render(request, f'{information_page.template}', context)

    else:
        context = {
            'error_code': 404,
            'message': 'Page request not found'
        }
        return render(request, 'expe/error.html', context)


def load_example_page(request, slug, session_id, progress_id):
    """Enable to load the information page before starting experiment
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':

        # access using unique slug
        experiment = Experiment.objects.get(slug=slug)
        session = Session.objects.get(id=session_id)
        example_page = experiment.example_page

        progress_class = utils.load_progress_class(session.progress_choice)
        
        progress = progress_class.objects.get(id=progress_id)

        # initialize and get all data fields
        progress.start(request.POST)

        context = {
            'page': example_page,
            'experiment': experiment, 
            'progress': progress,
            'session': session
        }
        
        # dynamic rendering with use of custom page template
        return render(request, f'{example_page.template}', context)

    else:
        context = {
            'error_code': 404,
            'message': 'Page request not found'
        }
        return render(request, 'expe/error.html', context)


def run_experiment_step(request, slug, session_id, progress_id):
    """Enable to process an experiment for the current participant progress 
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if request.method == 'POST':
        # access using unique slug
        experiment = Experiment.objects.get(slug=slug)
        session = Session.objects.get(id=session_id)
        main_page = experiment.main_page

        progress_class = utils.load_progress_class(session.progress_choice)
        
        progress = progress_class.objects.get(id=progress_id)

        # retrieve previous step if exists
        previous_step = None

        # process an experiment step only if data field is not None
        if not progress.is_started:
            progress.is_started = True
        else:
            previous_step = SessionStep.objects.filter(progress_id=progress.id).latest('created_on')

        # send previous step (if exists) and request dict form data
        step_data = progress.next(previous_step, request.POST)

        # create new state
        experiment_step = SessionStep.objects.create(
            progress=progress,
            data=step_data
        )

        # session = Session.objects.get(id=progress.session.id)
        # print(session.participants.all())
        # print('There is some expe steps:', SessionStep.objects.filter(progress_id=progress.id).all().count())

        if progress.end():
            
            # passed as finished state
            progress.is_finished = True
            progress.save()

            # remove from session
            del request.session['progress'][str(progress.session.id)]
            request.session.save()
            
            end_page = experiment.end_page

            context = {
                'page': end_page,
                'experiment': experiment, 
                'session': session,
                'progress': progress
            }

            return render(request, f'{end_page.template}', context)

        context = {
            'page': main_page,
            'experiment': experiment,
            'session': session,
            'progress': progress,
            'progress_info': int(progress.progress()),
            'step': experiment_step
        }
        
        # dynamic rendering with use of custom page template
        return render(request, f'{main_page.template}', context)
    else:
        context = {
            'error_code': 404,
            'message': 'Page request not found'
        }
        return render(request, 'expe/error.html', context)


def experiment_stat(request):
    """Check and add participant if not exist
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])

    experiment = None

    if 'slug' in request.POST:
        slug = request.POST['slug']
        try:        
            experiment = Experiment.objects.get(slug=request.POST['slug'])
        except:
            print(f'Cannot load experiment with slug: {slug}')

    if experiment is None:

        context = {
            'error_code': 404,
            'message': 'Page request not found'
        }
        return render(request, 'expe/error.html', context)

   
    # only the 3 with most stats info
    progress_data = {}
    for s in experiment.sessions.all():

        if s.is_available:
            progress_class = utils.load_progress_class(s.progress_choice)

            progresses = progress_class.objects.filter(session_id=s.id)

            progress_data[s.name] = {
                'count': progresses.count()
            }

    
    most_popular_sessions = sorted(progress_data, key=lambda k: progress_data[k]['count'], reverse=True)[:3]
    final_progress_data = {}

    for elem in most_popular_sessions:
        final_progress_data[elem] = {
                'count': progress_data[elem]['count']
            }

    return HttpResponse(json.dumps(final_progress_data), content_type="application/json")

@user_passes_test(lambda user: user.is_superuser)
def download_session_progresses(request, session_id):
    """Create JSON file as output and send it
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])

    session = Session.objects.get(id=session_id)

    progress_class = utils.load_progress_class(session.progress_choice)

    session_progresses = progress_class.objects.filter(session_id=session.id)
    
    data = {
        'experiment': session.experiment.title,
        'session': session.name,
        'number_of_participants': session_progresses.count(),
        'participations': []
    }

    for s_progress in session_progresses:

        # retrieve main information
        progress_data = {
            'participant_id': str(s_progress.participant.id),
            'created_on': s_progress.created_on.strftime('%A %d-%m-%Y, %H:%M:%S'),
            'participation_data': s_progress.data,
            'steps': []
        }
        # retrieve steps information
        steps = SessionStep.objects.filter(progress_id=s_progress.id)

        for step in steps:
            data_step = {
                'created_on': step.created_on.strftime('%A %d-%m-%Y, %H:%M:%S'),
                'data': step.data
            }

            progress_data['steps'].append(data_step)

        # finally add progress data into main returned data
        data['participations'].append(progress_data)

    if not os.path.exists(settings.OUPUT_DATA_FOLDER):
        os.makedirs(settings.OUPUT_DATA_FOLDER)
    # create output file
    json_filename = f'{session.experiment.title.replace(" ", "-").lower().strip()}__\
        {session.name.replace(" ", "-").lower().strip()}.json'

    # create file into specific data folder
    json_filepath = os.path.join(settings.OUPUT_DATA_FOLDER, json_filename)

    with open(json_filepath, 'w') as f:
        json.dump(data, f, indent=2)

    # return buffer data
    f = open(json_filepath, 'r')
    
    response = HttpResponse(f, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename={json_filename}'

    return response

def error_404(request, exception):
    """Create 404 error page
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    context = {
        'error_code': 404,
        'message': 'Page request not found'
    }
    print(f'Error encountered [404]: {exception}')
    return render(request, 'expe/error.html', context)


def error_500(request):
    """Create 500 error page
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    context = {
        'error_code': 500,
        'message': 'Server seems to encountered some issues, please wait'
    }
    print(f'Error encountered [500]')
    return render(request, 'expe/error.html', context)

def error_403(request, exception):
    """Create 403 error page
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    context = {
        'error_code': 403,
        'message': 'You do not have permissions for this page'
    }
    print(f'Error encountered [403]: {exception}')
    return render(request, 'expe/error.html', context)

def error_400(request, exception):
    """Create 400 error page
    Args:
        request ([Request]): Django request object with expected key and value data
    Returns:
        [HttpResponse]: Http response message
    """
    context = {
        'error_code': 400,
        'message': 'Server seems to encountered some issues, please wait'
    }
    print(f'Error encountered [400]: {exception}')
    return render(request, 'expe/error.html', context)