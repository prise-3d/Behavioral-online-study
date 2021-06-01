# main imports
import os
import time
import numpy as np
import pickle
import sys
import json

from datetime import datetime

# django imports
from django.conf import settings

# module imports
from .. import config as cfg

# expe imports
from .classes.quest_plus import QuestPlus
from .classes.quest_plus import psychometric_fun

# other imports 
from ipfml import utils
from pprint import pprint

from PIL import Image, ImageDraw

lang = settings.LANGUAGE_CODE
    
def run_quest_example(request, model_filepath, output_file):

    # 1. get session parameters
    expe_name = request.session.get('expe')
    
    # Check if values are correct:
    if 'expe_started' in request.session and request.session.get('expe_started') == True:
        def isint(s):
            try: 
                int(s)
                return True
            except ValueError:
                return False
    
        data_expe = request.session['expe_data']

        if not 'iteration' in request.GET or isint(request.GET.get('iteration')) == False:
            return data_expe
        
        if not 'answer' in request.GET or \
           isint(request.GET.get('answer')) == False or \
           (int(request.GET.get('answer')) != 0 and int(request.GET.get('answer')) != 1):
               return data_expe
           
        if not 'check' in request.GET or \
           (request.GET.get('check') != "true" and request.GET.get('check') != "false"):
               return data_expe
        
    checked = request.GET.get('check')

    # by default
    iteration = 0

    # used to stop when necessary
    if 'iteration' in request.GET:
        iteration = int(request.GET.get('iteration'))
    else:
        request.session['expe_started'] = False

    # 2. Get expe information if started
    # first time only init `quest`
    # if experiments is started we can save data
    if request.session.get('expe_started'):

         # does not change expe parameters
        if request.session['expe_data']['expe_previous_iteration']+1 != iteration:
            data_expe = request.session['expe_data']
            return data_expe
        elif iteration > cfg.expes_configuration[expe_name]['params']['max_iterations']:
            return None
        else:
            current_expe_data = request.session['expe_data']
            answer = int(request.GET.get('answer'))
            expe_answer_time = time.time() - current_expe_data['expe_answer_time']
            previous_stim = current_expe_data['expe_stim']

            print("Answer time is ", expe_answer_time)

    # 3. Load or create Quest instance
    # default params
    stim_space = np.arange(50, 20000, 100) 
    stim_space = np.append(stim_space, 20000)
    
    slopes = np.arange(0.0001, 0.001, 0.00003)

    # check if necessary to construct `quest` object
    if not os.path.exists(model_filepath):
        print('Creation of `qp` model')
        qp = QuestPlus(stim_space, [stim_space, slopes], function=psychometric_fun)

    else:
        print('Load `qp` model')
        filehandler = open(model_filepath, 'rb') 
        qp = pickle.load(filehandler)
        pprint(qp)
    
    #initialize entropy
    entropy = np.inf
    last_entropy = 0
    crit_entropy = cfg.expes_configuration[expe_name]['params']['entropy']
    min_iter = cfg.expes_configuration[expe_name]['params']['min_iterations']
    max_iter = cfg.expes_configuration[expe_name]['params']['max_iterations']
    
    # 4. If expe started update and save experiments information and model
    # if experiments is already began
    if request.session.get('expe_started'):

        # TODO : update norm slopes
        #previous_stim_norm = (int(previous_stim) - stim_space.min()) / (stim_space.max() - stim_space.min() + sys.float_info.epsilon)

        print(previous_stim)
        #print(previous_stim_norm)

        qp.update(int(previous_stim), answer) 
        threshold = qp.get_fit_params(select='mode')[0]
        
        entropy = qp.get_entropy()
        print('chosen entropy', entropy)

        line = str(previous_stim)
        line += ";" + str(answer) 
        line += ";" + str(expe_answer_time) 
        line += ";" + str(entropy)
        line += '\n'

        output_file.write(line)
        output_file.flush()
        
        entropies = np.loadtxt(output_file.name, delimiter=";", usecols=3, skiprows=1)

        if len(entropies.shape) > 0 and entropies.shape[0] >= 11:
            last_entropy = entropies[-11]
        else:
            last_entropy = np.nan

    # check time
    current_time = datetime.utcnow()
    current_time = time.mktime(current_time.timetuple())
    started_time = request.session.get('timestamp')
    started_time = time.mktime(datetime.strptime(started_time, "%Y-%m-%d_%Hh%Mm%Ss").timetuple())
    max_time = cfg.expes_configuration[expe_name]['params']['max_time'] * 60
    if current_time - started_time >= max_time:
        request.session['expe_finished'] = True
        timeout = { 'timeout' : True }
        return timeout

    # 5. Get next image depending of Quest model state
    # construct image 
    if iteration < min_iter or ((last_entropy is np.nan or np.abs(entropy - last_entropy) >= crit_entropy) and iteration < max_iter):
        # process `quest`
        if iteration <= 4:
            next_stim_id = int(iteration * len(stim_space)/10)
            next_stim = stim_space[next_stim_id]
        else:
            next_stim = qp.next_contrast()
        print(next_stim)
        #next_stim_img = int(next_stim*(stim_space.max()-stim_space.min())+stim_space.min())
    
        print('-------------------------------------------------')
        print(f'Iteration {iteration}')
        print(next_stim)
        #print('denorm', next_stim_img)
        print('-------------------------------------------------')


    else:
        request.session['expe_finished'] = True
        return cfg.expes_configuration[expe_name]['text']['end_text']

    # save image using user information
    # create output folder for tmp files if necessary
    tmp_folder = os.path.join(settings.MEDIA_ROOT, cfg.output_tmp_folder)

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    print(f'User id: {request.session.get("id")}')
    # generate tmp merged image (pass as BytesIO was complicated..)
    filepath_img = os.path.join(tmp_folder, request.session.get('id') + '_' + expe_name + '.png')
    
    # replace img_merge if necessary (new iteration of expe)
    current_image = Image.open(os.path.join(settings.RELATIVE_STATIC_URL, 'images', 'example_1.png'))

    if current_image is not None:
        current_image.save(filepath_img)

    # save qp model at each iteration
    file_pi = open(model_filepath, 'wb') 
    pickle.dump(qp, file_pi)

    # 6. Prepare experiments data for current iteration and data for view
    
    # here you can save whatever you need for you experiments
    data_expe = {
        'image_path': filepath_img,
        'expe_answer_time': time.time(),
        'expe_previous_iteration': iteration,
        'expe_stim': str(next_stim),
        'indication': cfg.expes_configuration[expe_name]['text']['indication']
    }
    
    # expe is now started
    request.session['expe_started'] = True

    return data_expe

def eval_quest_example(request, output_filename):
    expe_name = request.session.get('expe')
    lines = []
    with open(output_filename, 'r') as output_file:
        lines = output_file.readlines()
  
    iters = len(lines)-1
    if iters < cfg.expes_configuration[expe_name]['params']['min_iterations']:
        return False
    
    time=[]
    checkbox=[]
    nb_check=0
    for i in range(1,len(lines)):
        l = lines[i]
        line_split = l.split(";")
        time.append(float(line_split[6]))
        checkbox.append(line_split[8])
    time_total = np.sum(time)/60
    for i in range(cfg.expes_configuration[expe_name]['checkbox']['frequency']-1,len(checkbox),cfg.expes_configuration[expe_name]['checkbox']['frequency']):
        if checkbox[i]=='true\n':
            nb_check = nb_check + 1
    if nb_check < len(checkbox)/cfg.expes_configuration[expe_name]['checkbox']['frequency']:
        return False
    
    if time_total<7.:
        return False

