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
from .. import config as cfg # get config experiments parameters

# expe imports
from .classes.quest_plus import QuestPlus
from .classes.quest_plus import psychometric_fun

# other imports 
from pprint import pprint

from PIL import Image

def run_quest_example(request, model_filepath, output_file):
    """Run the experiment expected iteration process when client answer
    Saved data (Quest+ instance and output data) use the unique client ID

    Args:
        request [Request]: django request param
        model_filepath [str]: filetpath expected for the output Quest model linked to current client (where the model is saved)
        output_file [file buffer]: output file buffer of current client where new collected data line are saved

    Returns:
        [dict]: dictionnary of the experiment data state based on experiment process
    """

    print(f'Process experiment iteration for user id: {request.session.get("id")}')

    ##########
    # STEP 1. get session experiment name and static parameters
    ##########

    expe_name = request.session.get('expe')
    max_iterations = cfg.expes_configuration[expe_name]['params']['max_iterations']
    min_iterations = cfg.expes_configuration[expe_name]['params']['min_iterations']
    
    ##########
    # STEP 2. Check if values are correct:
    ##########

    if 'expe_started' in request.session and request.session.get('expe_started'):
    
        data_expe = request.session['expe_data']
        

        if not 'iteration' in request.GET or not request.GET.get('iteration').isdigit():
            return data_expe
        
        # Check expected answer value
        if not 'answer' in request.GET \
            or not request.GET.get('answer').isdigit() \
            or (int(request.GET.get('answer')) not in [0, 1]):

            return data_expe
           
    # Retrieve current iteration value
    iteration = 0

    # Iteration is used for experiment stopping criterion (see `max_iterations` from `expe/config.py` file)
    if 'iteration' in request.GET:
        iteration = int(request.GET.get('iteration'))
    else:
        request.session['expe_started'] = False

    ##########
    # STEP 3. Get expe information if started
    ##########

    if request.session.get('expe_started'):

        previous_iteration = None
        if 'expe_previous_iteration' in request.session['expe_data']:
            previous_iteration = request.session['expe_data']['expe_previous_iteration']

        print(f'previous iteration', previous_iteration)

        # Keep same experiment data (just client page refresh)
        if previous_iteration is not None and previous_iteration + 1 != iteration:
            data_expe = request.session['expe_data']
            return data_expe

        # bad number of iteration
        elif iteration > max_iterations:
            return None

        # get current experiment data
        # if experiments is started we can save data
        else:
            # TODO : get another way to compute experiment time
            current_expe_data = request.session['expe_data']
            answer = int(request.GET.get('answer'))
            expe_answer_time = time.time() - current_expe_data['expe_answer_time']
            previous_stim = current_expe_data['expe_stim']
            print("Answer time is ", expe_answer_time)

    ##########
    # STEP 4. Load or create Quest instance
    ##########

    # model instance with default params
    # TODO : replace with your expected Quest+ params (`stimulus space` and `slopes`)
    stim_space = np.arange(50, 20000, 100) 
    stim_space = np.append(stim_space, 20000)
    
    slopes = np.arange(0.0001, 0.001, 0.00003)

    # check if necessary to construct `quest` object
    if not os.path.exists(model_filepath):
        print('Creation of `qp` model')
        qp = QuestPlus(stim_space, [stim_space, slopes], function=psychometric_fun)

    # if model exists, just necessary to load its binary state 
    else:
        print('Load `qp` model')
        filehandler = open(model_filepath, 'rb') 
        qp = pickle.load(filehandler)
        pprint(qp)
    
    # Initialize and get experiment configuration parameters
    entropy = np.inf
    last_entropy = 0

    crit_entropy = cfg.expes_configuration[expe_name]['params']['entropy']
    
    ##########
    # STEP 5. If expe started update, save experiments information and model
    ##########

    # if experiments is already began
    if request.session.get('expe_started'):

        # update model using client answer
        qp.update(int(previous_stim), answer) 
        threshold = qp.get_fit_params(select='mode')[0]
        
        # get new entropy
        entropy = qp.get_entropy()
        print(f'Quest+ model updated: chosen entropy {entropy} and threshold {threshold}')

        # log trace of current model updates
        line = str(previous_stim)
        line += ";" + str(answer) 
        line += ";" + str(expe_answer_time) 
        line += ";" + str(entropy)
        line += '\n'

        output_file.write(line)
        output_file.flush()
        
    ##########
    # STEP 6. check experiment timeout
    ##########
    current_time = datetime.utcnow()
    current_time = time.mktime(current_time.timetuple())
    started_time = request.session.get('timestamp')
    started_time = time.mktime(datetime.strptime(started_time, "%Y-%m-%d_%Hh%Mm%Ss").timetuple())
    
    max_time = cfg.expes_configuration[expe_name]['params']['max_time'] * 60

    # return time out data if end of experiment
    if current_time - started_time >= max_time:
        print('Timeout is reached')
        return { 'timeout' : True }

    ##########
    # STEP 7. Get next image depending of Quest model state
    ##########

    # check Quest+ stopping criterion
    if iteration < min_iterations \
        or ((last_entropy is np.nan or np.abs(entropy - last_entropy) >= crit_entropy) and iteration < max_iterations):

        # process `quest`
        if iteration <= 4:
            next_stim_id = int(iteration * len(stim_space)/10)
            next_stim = stim_space[next_stim_id]
        else:
            next_stim = qp.next_contrast()
    
        print('-------------------------------------------------')
        print(f'Iteration {iteration}')
        print(next_stim)
        print('-------------------------------------------------')

        # TODO : add your new image to display depending of Quest+ state
        # Here the current image is static
        # TODO : add basic exemple of experiment
        current_image = Image.open(os.path.join(settings.RELATIVE_STATIC_URL, 'images', 'example_1.png'))


    # one stopping criterion reached, end of the experiment
    else:
        request.session['expe_finished'] = True
        return cfg.expes_configuration[expe_name]['text']['end_text']

    ##########
    # STEP 8. Prepare new image to display to client part (`current_image` PIL variable)
    ##########

    # save image using user information
    # create output folder for tmp files if necessary
    tmp_folder = os.path.join(settings.MEDIA_ROOT, cfg.output_tmp_folder)

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    # generate tmp merged image
    filepath_img = os.path.join(tmp_folder, f'{request.session.get("id")}_{expe_name}.png')

    if current_image is not None:
        current_image.save(filepath_img)

    ##########
    # STEP 8. Save new state of user Quest+ model instance
    ##########
    # save qp model at each iteration
    file_pi = open(model_filepath, 'wb') 
    pickle.dump(qp, file_pi)


    ##########
    # STEP 9. Prepare experiments data for current iteration and data for view
    ##########
    
    # TODO: here you can save whatever you need for you experiments
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