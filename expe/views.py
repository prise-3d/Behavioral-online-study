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
from .utils import functions

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


def update_session_user_id(request):
    """Update user identifier

    Args:
        request ([Request]): Django request object

    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])

    request.session['id'] = request.POST.get('value')
    return HttpResponse('`user_id` session update done')


def update_session_user_expes(request):
    """Update user experiment data
    This function can be use to store into `user_expes` all required data you want

    Args:
        request ([Request]): Django request object

    Returns:
        [HttpResponse]: Http response message
    """
    if not request.method =='POST':
        return HttpResponseNotAllowed(['POST'])

    request.session['user_expes'] = request.POST.get('value')
    return HttpResponse('`user_expes` session update done')


def expe_list(request):
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
    data = get_base_data()

    data['choice']  = cfg.label_expe_list
    data['submit']  = cfg.submit_button

    return render(request, 'expe/expe_list.html', data)


def presentation(request):
    # get param 
    expe_name = request.GET.get('expe')
    
    # always get base data
    data = get_base_data()
    
    data['expe_name'] = expe_name
    data['pres_text'] = cfg.expes_configuration[expe_name]['text']['presentation']
    data['next'] = cfg.expes_configuration[expe_name]['text']['next']
    
    return render(request, 'expe/expe_presentation.html', data)
    
# Create your views here.
def expe(request):
    
    # get param 
    expe_name = request.GET.get('expe')
    
    # unique user ID during session (user can launch multiple exeperiences)
    if 'id' not in request.session:
        request.session['id'] = functions.uniqueID()

    # first time expe is launched add expe information into session
    if 'expe' not in request.session or expe_name != request.session.get('expe'):
        refresh_data(request, expe_name)

    # create output folder for expe_result
    current_day = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")

    user_identifier = request.session.get('id')
    
    #check if it's the beginning
    if 'results_folder' not in request.session:
        output_expe_folder = cfg.output_expe_folder_name_day.format(expe_name, current_day, user_identifier)
                
        results_folder = os.path.join(settings.MEDIA_ROOT, output_expe_folder)
        request.session['results_folder'] = results_folder
    else:
        results_folder = request.session.get('results_folder')
    
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    result_filename = request.session.get('timestamp') +".csv"
    results_filepath = os.path.join(results_folder, result_filename)
    
    result_structure = request.session.get('timestamp') +".json"
    result_structure = os.path.join(results_folder, result_structure)
    
    request.session['result_structure'] = result_structure

    if not os.path.exists(results_filepath):
        output_file = open(results_filepath, 'w')
        functions.write_header_expe(output_file, expe_name)
    else:
        output_file = open(results_filepath, 'a')
        
    if not os.path.exists(result_structure):
        
        metadata = {
            "user_identifier": user_identifier,
            "min_iter" : cfg.expes_configuration[expe_name]['params']['min_iterations'],
            "max_iter" : cfg.expes_configuration[expe_name]['params']['max_iterations'],
            "crit_entropy" : cfg.expes_configuration[expe_name]['params']['entropy'],
            'terminated': False
        }

        with open(result_structure, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
    

    # TODO : add crontab task to erase generated img and model data
    # create `quest` object if not exists    
    models_folder = os.path.join(settings.MEDIA_ROOT, cfg.model_expe_folder.format(expe_name, current_day))

    if not os.path.exists(models_folder):
        os.makedirs(models_folder)

    model_filename = result_filename.replace('.csv', '.obj')
    model_filepath = os.path.join(models_folder, model_filename)

    # run expe method using `expe_name`
    function_name = 'run_' + expe_name

    try:
        run_expe_method = getattr(run_expe, function_name)
    except AttributeError:
        raise NotImplementedError("Run expe method `{}` not implement `{}`".format(run_expe.__name__, function_name))

    expe_data = run_expe_method(request, model_filepath, output_file)

    # set expe current data into session (replace only if experiments data changed)
    if expe_data is not None:
        request.session['expe_data'] = expe_data

        # get base data
    data = get_base_data(expe_name)
    
    # other experimentss information
    data['expe_name']   = expe_name
    data['userId']      = user_identifier

    if expe_data is not None and 'timeout' in expe_data and expe_data['timeout'] == True:
        result_structure = request.session.get('result_structure')
        metadata = {}
        with open(result_structure, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        metadata['timeout'] = True
        metadata['terminated'] = True
        metadata['reject'] = False
        with open(result_structure, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        data['timeout'] = True
        data['end_text']  = cfg.expes_configuration[expe_name]['text']['end_text']['timeout']
        clear_session(request)
        return render(request, 'expe/expe_end.html', data)

    else:
        data['end_text'] = cfg.expes_configuration[expe_name]['text']['end_text']['classic']
            
    request.session['end_text'] = data['end_text']

    return render(request, cfg.expes_configuration[expe_name]['template'], data)

def clear_session(request):
    expe_name = request.session.get('expe')

    del request.session['expe']
    del request.session['timestamp']
    del request.session['end_text']
    del request.session['results_folder']

    # specific current expe session params (see `config.py`)
    for key in cfg.expes_configuration[expe_name]['session_params']:
        del request.session[key]

def expe_end(request):
    expe_name = request.session.get('expe')
    
    # expe is ended before we can now reinit experiment
    request.session['expe_finished'] = False
    request.session['expe_started'] = False

    result_structure = request.session.get('result_structure')
    metadata = {}
    with open(result_structure, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    metadata['condition'] = request.GET.get('condition')
    metadata['dark'] = request.GET.get('dark')
    metadata['glasses'] = request.GET.get('glasses')
    metadata['trust'] = request.GET.get('trust')
    metadata['attention'] = request.GET.get('attention')
    
    with open(result_structure, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    data = get_base_data()
    data['userId'] = request.session.get('id')    
    data['end_text'] = request.session.get('end_text')
    data['expe_name'] = expe_name

    print('End of experiment =>', request.session)
    
    results_folder = request.session.get('results_folder')
    result_filename = request.session.get('timestamp') +".csv"
    results_filepath = os.path.join(results_folder, result_filename)

    # reinit session as default value
    # here generic expe params
    if 'expe' in request.session:
        clear_session(request)

    return render(request, 'expe/expe_end.html', data)


@login_required(login_url="login/")
def list_results(request, expe=None):
    """
    Return all results obtained from experiments
    """

    valid_color = "green"
    timeout_color = "blue"
    unterm_color = "red"
    reject_color = "magenta"
    colors = {
            'validated': valid_color, 
            'timeout': timeout_color, 
            'rejected': reject_color, 
            'unterminated': unterm_color
            }

    def create_file_color(filenames):
        files = {}
        json_files = [f for f in filenames if f.endswith("json")]
        for json_file in json_files:
            csv_file = os.path.splitext(json_file)[0] + ".csv"

            metadata = {}
            with open(os.path.join(user_path, json_file), 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            if 'terminated' not in metadata or metadata['terminated'] == False:
                files[json_file] = unterm_color
                files[csv_file] = unterm_color

            elif metadata['timeout'] == True:
                files[json_file] = timeout_color
                files[csv_file] = timeout_color

            elif metadata["reject"] == True:
                files[json_file] = reject_color
                files[csv_file] = reject_color

            else:
                files[json_file] = valid_color
                files[csv_file] = valid_color      

        return files

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
                        folders_user[user] = create_file_color(filenames)

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
                            folders_user[user] = create_file_color(filenames)

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
    data['colors'] = colors
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
    '''
    Utils method to refresh data from session
    '''
    request.session['expe'] = expe_name

    request.session['expe_started'] = False
    request.session['expe_finished'] = False

    # update unique timestamp each time new experiments is launched
    request.session['timestamp'] = datetime.strftime(datetime.utcnow(), "%Y-%m-%d_%Hh%Mm%Ss")