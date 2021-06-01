# main imports
import os

# folder variables
# TODO : dispatch into day and experiment ID
model_expe_folder              = "expes_models/{0}/{1}"
output_expe_folder             = "expes_results"
output_expe_folder_date        = "expes_results/date"
output_expe_folder_id          = "expes_results/expeId"
output_expe_folder_name_id_day = "expes_results/expeId/{0}/{1}/{2}/{3}"
output_expe_folder_name_day    = "expes_results/date/{0}/{1}/{2}"
output_tmp_folder              = "tmp"

# expes list
label_expe_list                =  'Select an experiment'
submit_button                  =  'Submit'

expe_name_list                 = ["quest_example"]

# configure experiments labels
expes_configuration            = {

    # First experiments configuration
    'quest_example':{
        # do not forget to add slopes and new scenes is added for this experiment
        'expected_duration': 30,

        'text':{
            'next' : "Please press enter to continue",
            'presentation' : "This is an example of experiment",
            'question': "Do you think that you are viewing a single image with the same quality everywhere",
            'end_text': {
                'classic': "Experience is finished. Thanks for your participation!",
                'timeout': "Unfortunately, the maximum duration to conclude the experiment has been reached.",
            },
        },
        'params':{
            'min_iterations': 10,
            'max_iterations': 15,
            'max_time': 10, # 10 minutes
            'entropy': 0.05, # quest stopping criterion
        },
    
        # if others custom session param are directly set for experiments
        'session_params': [
            'expe_data',
        ],

        # template file used in django `expe` route
        'template': 'expe/expe.html',

        # javascript file used
        'javascript':[
            'loadImg.js',
            'keyEvents.js'
        ],
        'output_header': 
            "stimulus;name_stimulus;cropping_percentage;orientation;image_ref_position;answer;time_reaction;entropy;checkbox\n",
    }
}
