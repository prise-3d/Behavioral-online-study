# Create your own expe

## Description

This website can let you create and manage your own experimentss 

## Explanations

The `expe` module is the django app created for managing experimentss.

- `expe/config.py`: contains the main variables used by website, save experimentss content and experimentss configuration.
- `expe/views.py`: is django app file used for enable routes of website.
- `expe/expes/run.py`: contains **run** functions in order to launch step of experiments.
- `expe/expes/classes`: is folder which contains all the necessary Python classes for experimentss.

## Create your own experiments

### 1. Experience configuration

Let's start with the `expe/config.py` python file. As explained earlier, this file contains experimentss configuration. The variable `expes_configuration` is the dictionnary which declares all information of experimentss.

An example for the `quest_one_image` key experiments:

```python
'quest_one_image':{
    'text':{
        'question': "Do you see one image or a composition of more than one?",
        'indication': "press left if you see one image, right if not",
        'end_text': "Experience is finished. Thanks for your participation",
    },
    'params':{
        'iterations': 10
    },

    # if others custom session param are directly set for experiments
    'session_params': [
        'expe_data',
    ],

    # template file used in django `expe` route
    'template': 'expe/expe.html',

    # javascript file used
    'js':[
        'loadImg.js',
        'keyEvents.js'
    ],
    'output_header': "stimulus;name_stimulus;cropping_percentage;...\n"
}
```

The `params` section is where you put all your necessary information for your experiments.

### 2. The experiments `expe` route

The `expe/` route define by the `expe` function in `expe/views.py` is used to launch experiments. This route uses few parameters pass using GET method:
- `expe`: the experiments name to use
- `scene`: the scene name to use for this experiments
- `iteration`: step of this experiments
- `answer`: the answer of the user

Using this parameter, the route know which experiments to launch with specific scene and manage experiments steps.

**Note:** `answer` and `iteration` parameters are used into `js/keyEvents.js` file. This means the `answer` and `iteration` values are sent depending of user interactions. You can implement your own interaction by creating your own `js` file and add it into your experiments configuration declaration (see `expe/config.py`).

### 3. The `run` experiments function

Into the `expe` function in `expe/views.py`, the `run` method your experiments is dynamically call. Hence you need to implement into the `expe/expes/run.py` a function which follow this naming convention:

- `run_{{you_experiments_name}}`

As you have communication exchanges between the django server and the client side, it's necessary to store the experiments process at each step.

Hence, this function need to follow this prototype:

```python
def run_experiments_name(request, model_filepath, output_file):
```

Information about parameters:
- `request`: contains all information into GET, POST and session storages
- `model_filepath`: filename where you need to store information about experiments model into a binary file (can be just data information or object instanciated from file of `expe/expes/classes`)
- `output_file`: buffer where you can add information about your experiments (following your `output_header` declared into your experiments configuration)


Example of accessing request variables:
```python
expe_name_session = request.session.get('expe')
expe_name_get     = request.GET.get('expe')
expe_name_post    = request.POST.get('expe')
```

Example of loading or saving Python object (need of pickle):
```python
# check if necessary to construct `quest` object or if backup exists
if not os.path.exists(model_filepath):
    qp = QuestPlus(stim_space, [stime_space, slopes], function=psychometric_fun)
else:
    print('Load `qp` model')
    filehandler = open(model_filepath, 'rb') 
    qp = pickle.load(filehandler)
``` 

```python
# save `quest` model
file_pi = open(model_filepath, 'wb') 
pickle.dump(qp, file_pi)
```

Example of writing and append information into `output_file`:

```python
line = str(previous_stim)
line += ";" + str(answer) 
line += ";" + str(expe_answer_time) 
line += ";" + str(entropy) 
line += '\n'

output_file.write(line)
output_file.flush()
```

### 5. Display experiments data into custom template

Finally your `run` function need to return python dictionnary of data your need to use into your `expe/` django template. 

If you want to create your own template, specify your template path into configuration:

```python
'experiments_name':{
    ...
    # template file used in django `expe` route
    'template': 'expe/my_expe_template.html',
    ...
}
```

Example of way to use your experiments data into template:
```python
{{request.session.expe_data|get_value_from_dict:'image_path'}}
```
