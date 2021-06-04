# django imports
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseNotAllowed
from django.conf import settings

# main imports
import os
import json
import base64
import random
import numpy as np
from datetime import datetime
import pickle 
import time
import zipfile
from io import BytesIO


# expe imports
from .expes.classes.quest_plus import QuestPlus
from .expes.classes.quest_plus import psychometric_fun

from .expes import run as run_expe

# image processing imports
import io
from PIL import Image, ImageDraw

# module imports
from . import utils # load utils fucntions 

from . import config as cfg

def get_base_data(expe_name=None):
    """Get required data to store into request (for each request)

    Args:
        expe_name ([str], optional): Experiment name. Defaults to None.

    Returns:
        [dict]: required data to add into request
    """
    data = {}

    # if expe name is used include required Javascript file from configuration
    if expe_name is not None:
        data['javascript'] = cfg.expes_configuration[expe_name]['javascript']

    expes = cfg.expe_name_list

    # expe data
    data['expes'] = expes

    # Display experiment names for Django to Javascript transmission
    data['expes_names'] = json.dumps(expes)

    return data


def update_session_user(request):
    """Update user session data

    Args:
        request ([Request]): Django request object with expected key and value data

    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])

    key = request.POST.get('key')

    request.session[key] = request.POST.get('value')
    return HttpResponse('session update done')


def expe_list(request, data=None):
    """Default home page with experiment list option

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new page to render with data
    """

    # by default user restart expe
    request.session['expe_started'] = False
    request.session['expe_finished'] = False

    if 'results_folder' in request.session:
        del request.session['results_folder']
    
    # always get base data
    if data is not None:
        data = utils.merge_data(data, get_base_data())
    else:
        data = get_base_data()

    data['choice']  = cfg.label_expe_list
    data['submit']  = cfg.submit_button

    return render(request, 'expe/expe_list.html', data)


def presentation(request):
    """Add presentation of the example experiment

    Args:
        request ([Request]): Django request instance

    Returns:
        [Template]: new presentation page to render with data
    """
    # get param 
    expe_name = request.GET.get('expe')
    
    # always get base data
    data = get_base_data()
    
    data['expe_name'] = expe_name
    data['pres_text'] = cfg.expes_configuration[expe_name]['text']['presentation']
    data['question'] = cfg.expes_configuration[expe_name]['text']['question']
    data['indication'] = cfg.expes_configuration[expe_name]['text']['indication']
    data['next'] = cfg.expes_configuration[expe_name]['text']['next']

    # First time expe is launched add expe information into session
    # here we refresh the session as a new experiment
    refresh_data(request, expe_name)
    
    return render(request, 'expe/expe_presentation.html', data)
    
# Create your views here.
def expe(request):
    
    ######
    # STEP 1. Get expe name param 
    ######
    expe_name = request.GET.get('expe')
    
    #####
    # STEP 2. Initialize experiment data for user
    #####

    # Unique user ID during session (user can launch multiple exeperiences)
    # Unique user ID is saved into local storage inside browser. The unique ID enable to know the current user even if new connexion
    # See more information in: https://developer.mozilla.org/fr/docs/Web/API/Window/localStorage
    if 'id' not in request.session:
        request.session['id'] = utils.uniqueID()

    # if experiment not began, by default redirect to home
    if 'expe' not in request.session or expe_name != request.session.get('expe'):
        return expe_list(request, {})

    # create output folder for expe_result
    current_day = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")

    user_identifier = request.session.get('id')
    
    # Create if not exists custom result folder name depending of Experiment, Day, and User ID
    if 'results_folder' not in request.session:
        output_expe_folder = cfg.output_expe_folder_name_day.format(expe_name, current_day, user_identifier)
                
        results_folder = os.path.join(settings.MEDIA_ROOT, output_expe_folder)
        request.session['results_folder'] = results_folder # store into session
    else:
        results_folder = request.session.get('results_folder') # extract if already exists
    
    #####
    # STEP 3. Prepare log data for current experiment of user
    #####

    # create empty directory if not exists
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # create data log of each answer of user
    result_filename = request.session.get('timestamp') +".csv"
    results_filepath = os.path.join(results_folder, result_filename)
    
    # create json file with additional data from experiment
    result_structure = request.session.get('timestamp') +".json"
    result_structure = os.path.join(results_folder, result_structure)
    
    request.session['result_structure'] = result_structure

    # create csv data file with header if necessary
    if not os.path.exists(results_filepath):
        output_file = open(results_filepath, 'w')
        utils.write_header_expe(output_file, expe_name)
    else:
        output_file = open(results_filepath, 'a')
        
    # log basic additional information into JSON 
    if not os.path.exists(result_structure):
        
        metadata = {
            "user_identifier": user_identifier,
            "min_iter" : cfg.expes_configuration[expe_name]['params']['min_iterations'],
            "max_iter" : cfg.expes_configuration[expe_name]['params']['max_iterations'],
            "crit_entropy" : cfg.expes_configuration[expe_name]['params']['entropy'],
            'terminated': False
        }

        utils.update_json_file(result_structure, metadata)
    
    #####
    # STEP 4. Take care of where we save the Quest+ model instance
    #####

    # create `quest` object if not exists    
    models_folder = os.path.join(settings.MEDIA_ROOT, cfg.model_expe_folder.format(expe_name, current_day, user_identifier))

    if not os.path.exists(models_folder):
        os.makedirs(models_folder)

    # create model filepath
    model_filename = result_filename.replace('.csv', '.obj')
    model_filepath = os.path.join(models_folder, model_filename)


    #####
    # STEP 5. Run of the iteration method of the current experiment
    #         From `expe/expes/run.py`
    #####

    # run expe method using `expe_name` and dynamically call the model
    function_name = 'run_' + expe_name

    try:
        run_expe_method = getattr(run_expe, function_name)
    except AttributeError:
        raise NotImplementedError("Run expe method `{}` not implement `{}`".format(run_expe.__name__, function_name))

    # call the method
    # - Pass the output expected model path
    # - Pass the current output data buffer file
    expe_data = run_expe_method(request, model_filepath, output_file)

    # set new expe data obtained into session (replace only if experiments data changed)
    if expe_data is not None:
        request.session['expe_data'] = expe_data

    #####
    # STEP 6. Prepare output data and check how the experiment has terminated
    #         - Check if experiment end depending of timeout
    #         - Check if experiment terminated as expected
    #####

    # get base data
    data = get_base_data(expe_name)
    
    # other experiments information
    data['expe_name']   = expe_name
    data['userId']      = user_identifier

    # depending of timeout or not prepare end text and/or redirection
    if expe_data is not None and 'timeout' in expe_data and expe_data['timeout'] == True:

        print('Timeout detected')
        result_structure = request.session.get('result_structure')
        metadata = {}
        with open(result_structure, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        utils.update_json_file(result_structure, {'timeout': True, 'finished': False})

        data['timeout'] = True


        data['end_text']  = cfg.expes_configuration[expe_name]['text']['end_text']['timeout']
        
        # end of experiment, we can clear the experiment data
        clear_session(request)

        return expe_list(request, data)

    # clear also session if expe is finished normally
    if 'expe_finished' in request.session and request.session['expe_finished'] == True:
        
        clear_session(request)

        utils.update_json_file(result_structure, {'finished': True})

        data['end_text'] = expe_data['end_text']

        return expe_list(request, data)

    # by default indication and question
    data['question']   = cfg.expes_configuration[expe_name]['text']['question']
    data['indication'] = cfg.expes_configuration[expe_name]['text']['indication']

    return render(request, cfg.expes_configuration[expe_name]['template'], data)


def clear_session(request):
    """Clear the default session data added when experiment ended (and also experiment data added from `run` experiment session)
    See `expe.expes.run.py` methods for further information

    Args:
        request ([Request]): Django request instance
    """
    expe_name = request.session.get('expe')

    del request.session['expe']
    del request.session['timestamp']
    del request.session['results_folder']

    # specific current expe session params (see `config.py`)
    for key in cfg.expes_configuration[expe_name]['session_params']:
        del request.session[key]


@login_required(login_url="login/")
def list_results(request, expe=None):
    """
    Return all results obtained from experiments
    """

    if expe is None:
        folders = cfg.expe_name_list

        return render(request, 'expe/expe_results.html', {'expe': expe, 'folders': folders})

    else:
        if expe in cfg.expe_name_list:

            folder_date_path = os.path.join(settings.MEDIA_ROOT, cfg.output_expe_folder_date, expe)
            folder_id_path   = os.path.join(settings.MEDIA_ROOT, cfg.output_expe_folder_id, expe)

            # extract folder for user ID
            folder_user_id = {}

            # extract date files
            folders_date = {}

            if os.path.exists(folder_date_path):

                days = sorted(os.listdir(folder_date_path), reverse=True)

                # get all days
                for day in days:
                    day_path = os.path.join(folder_date_path, day)
                    users = os.listdir(day_path)

                    folders_user = {}
                    # get all users files
                    for user in users:

                        # add to date
                        user_path = os.path.join(day_path, user)
                        filenames = os.listdir(user_path)
                        folders_user[user] = filenames

                        # add to userId
                        if user not in folder_user_id:
                            folder_user_id[user] = {}
                            
                        if 'date' not in folder_user_id[user]:
                            folder_user_id[user]['date'] = {}

                        if day not in folder_user_id[user]['date']:
                            folder_user_id[user]['date'][day] = folders_user[user]

                             
                    # attach users to this day
                    folders_date[day] = folders_user

            # extract expe id files
            folders_id = {}

            if os.path.exists(folder_id_path):
                
                ids = sorted(os.listdir(folder_id_path), reverse=True)

                # get all days
                for identifier in ids:
                    id_path = os.path.join(folder_id_path, identifier)
                    days = sorted(os.listdir(id_path), reverse=True)

                    folder_days = {}
                    # get all days
                    for day in days:
                        day_path = os.path.join(id_path, day)
                        users = os.listdir(day_path)

                        folders_user = {}
                        # get all users files
                        for user in users:

                            user_path = os.path.join(day_path, user)
                            filenames = os.listdir(user_path)
                            folders_user[user] = filenames

                            # add filepaths to user id
                            if user not in folder_user_id:
                                folder_user_id[user] = {}
                            
                            if 'expeid' not in folder_user_id[user]:
                                folder_user_id[user]['expeid'] = {}

                            if identifier not in folder_user_id[user]['expeid']:
                                folder_user_id[user]['expeid'][identifier] = {}

                            if day not in folder_user_id[user]['expeid'][identifier]:
                                folder_user_id[user]['expeid'][identifier][day] = folders_user[user]
                        
                        # attach users to this day
                        folder_days[day] = folders_user

                    folders_id[identifier] = folder_days

            folders = { 'date': folders_date, 'expeId': folders_id, 'users': folder_user_id}
        else:
            raise Http404("Expe does not exists")

    # get base data
    data = get_base_data()
    # expe parameters
    data['expe']    = expe
    data['folders'] = folders
    data['infos_question']   = cfg.expes_configuration[expe]['text']['question']
    data['infos_indication']   = cfg.expes_configuration[expe]['text']['indication']

    return render(request, 'expe/expe_results.html', data)


@login_required(login_url="login/")
def download_result(request):
    
    path = request.POST.get('path')
    folder_path = os.path.join(settings.MEDIA_ROOT, cfg.output_expe_folder, path)

    # Folder is required
    if os.path.exists(folder_path):

        # Open BytesIO to grab in-memory ZIP contents
        s = BytesIO()

        # check if file or folder
        if os.path.isdir(folder_path):
            
            # get files from a specific day
            filenames = os.listdir(folder_path)

            # Folder name in ZIP archive which contains the above files
            # E.g [thearchive.zip]/somefiles/file2.txt
            # FIXME: Set this to something better
            zip_subdir = folder_path.split('/')[-1]
            zip_filename = "%s.zip" % zip_subdir

            # The zip compressor
            zf = zipfile.ZipFile(s, "w")

            for fpath in filenames:
                
                fpath = os.path.join(folder_path, fpath)

                # Calculate path for file in zip
                fdir, fname = os.path.split(fpath)
                zip_path = os.path.join(zip_subdir, fname)

                # Add file, at correct path
                zf.write(fpath, zip_path)

            # Must close zip for all contents to be written
            zf.close()

            output_filename = zip_filename
            content = s.getvalue()

        else:
            
            with open(folder_path, 'rb') as f:
                content = f.readlines()

            # filename only
            fdir, fname = os.path.split(path)
            output_filename = fname

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = HttpResponse(content, content_type="application/gzip")
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % output_filename

        return resp

    else:
        return Http404("Path does not exist")



def refresh_data(request, expe_name):
    """Utils method to refresh data from session when new experiment is launched

    Args:
        request ([type]): [description]
        expe_name ([str]): the expected experiment name
    """

    print('New session data')
    request.session['expe'] = expe_name

    # Set experiment as new experiment
    request.session['expe_started'] = False
    request.session['expe_finished'] = False

    # update unique timestamp each time new experiment is launched
    request.session['timestamp'] = datetime.strftime(datetime.utcnow(), "%Y-%m-%d_%Hh%Mm%Ss")