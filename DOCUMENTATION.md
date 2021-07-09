# Documentation and tutorial (create your own experiment)

## Description

This website allows you to create and manage your own psychophysical experiments using Python as a backend. 

Why such an application? Many experimental developments are done in Python, you can quickly include libraries and/or features developed in Python to create your experiments.

For a better understanding of this documentation, the user is invited to have a minimal knowledge of the use of the Django : [Django documentation](https://docs.djangoproject.com/en/3.2/).

## Explanations

The `expe` module is the Django app created for managing experiments.

Main app folders:
- `expe/config.py`: contains the main variables used by the website, to save the content of the experiments and the configuration of the experiments;
- `expe/views.py`: is the Django application file used to activate the website routes;
- `expe/expes/run.py`: contains **run_{expe_name}** functions in order to launch dynamically step of experiments;
- `expe/expes/classes`: contains **run_{expe_name}** functions to dynamically launch experimental steps;
- `expe/expes/templates`: is the folder that contains all `.html' templates with Django script variables displayed;
- `expe/expes/urls.py`: binds url routes with `views.py` functions (POST or GET methods).

Other folders:
- `static`: contains static resources useful for the website, such as images, as well as "css" and "js" resources;
- `media`: generated experiment files, such as the log file, the Quest+ model status binary file recorded when users pass experiments.

**Note**: We will discuss in more detail the subtleties of using javascript and Django's request and session variables.

## Create your own experiments

### 1. Experience configuration

Let's start with the python file `expe/config.py`. As explained earlier, this file contains the configuration of the experiments. The `expes_config` variable is the dictionary that declares all the information for the experiments.

An overview of the configuration of the `quest_example` experiment:

```python
'quest_example':{
    'text':{
        'question': "Do you think image still contains noise?",
        'indication': "Press the LEFT key if you think the image is not noisy, or the RIGHT key if you think the image is noisy.",
        'end_text': "Experience is finished. Thanks for your participation",
        ...
    },
    ...
    'params':{
        'min_iterations': 10,
        'max_iterations': 15,
        'max_time': 10, # 10 minutes
        'entropy': 0.05, # quest stopping criterion
    },

    # if other custom session settings are directly defined for the experiments
    'session_params': [
        'expe_data',
    ],

    # template file used in Django `expe` route. Specific to the declared experimentation
    'template': 'expe/expe.html',

    # javascript file used for experiment iteration
    'js':[
        'loadImg.js',
        'keyEvents.js'
    ],
    # specific output header when logging experiment data
    'output_header': "stimulus;...;entropy\n" 
}
```

The `params` section is where you put all the necessary information for your experiments.

### 2. The experiments `expe` route

The `expe/` route defined by the `expe` function in `expe/views.py` is used to perform experiments. This route uses some parameters passed by the `GET` method:
- `expe`: the current experiment name to use;
- `iteration`: step of the experiment;
- `answer`: the user's answer.

Thanks to this parameter, the route knows which experiments to launch with a specific scene and manages the stages of the experiments.

**Note:** The `answer` and `iteration` parameters are used in the `js/keyEvents.js` file. This means that the `answer` and `iteration` values are sent based on the user's interactions. You can implement your own interaction by creating your own `js` file and adding it to the configuration statement of your experiments (see `expe/config.py`).

### 3. The "run" function of an experiment

In the `expe` function of `expe/views.py`, the `run` method of your experiment is based on a dynamic call. You must therefore implement a function in the `expe/expes/run.py` file that follows this naming convention:

- `run_{your_experiment_name}`

From this function you have information communication exchanges between the Django server and the client side, it is necessary to store the experimentation process at each step.

Therefore, this function must follow this prototype:

```python
def run_{your_experiment_name}(request, model_filepath, output_file):
```

Parameter information:
- `request`: contains all the information from the `GET`, `POST` and session protocols.
- `model_filepath`: filename where the user-related experience model (like Quest+ or whatever you want) is stored in a binary file (can be just data information or an object instantiated from the `expe/expes/classes` file)
- `output_file`: buffer where you can add information about your experiments (depending on your `output_header` declared in your experiment configuration in `expe/config.py`)


Example of access to request variables :
```python
expe_name_session = request.session.get('expe')
expe_name_get     = request.GET.get('expe')
expe_name_post    = request.POST.get('expe')
```

Example of loading or saving a Python Quest+ object (the serialization library [pickle](https://docs.python.org/3/library/pickle.html) is required):
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

Example of writing and adding information to the buffer file `output_file`:

```python
line = str(previous_stim)
line += ";" + str(answer) 
line += ";" + str(expe_answer_time) 
line += ";" + str(entropy) 
line += '\n'

output_file.write(line)
output_file.flush()
```

### 4. Display experiments data into custom template

Finally, your `run` function should return a python dictionary of **data** that you should use in your Django `expe/` model. 

There are several types of information accessible from the Django model, it is important to differentiate between them:

- Query data:** the set of data (dictionary) sent by the query when choosing the rendered model;
- Session**: for information more related to the context of the experiment and not only to the current query, it is possible to store data in the session. In this way, within the html template, it is possible to retrieve, display and process data from the user's session. 

If you want to create your own html template, specify the path to your template in the :
```python
'experiments_name':{
    ...
    # template file used in django `expe` route
    'template': 'expe/my_expe_template.html',
    ...
}
```

**Some examples**:

Example of way to use your experiments current request data with safe display (html encoding) into template:
```python
<h2>Expe {{expe_name}}</h2>
```

Example of how to use the current demand data of your experiences with a safe display (html encoding) in the template:
```python
{{end_text | safe}}
```

Example of how to use the data from your experimental session and access a specific dictionary key in the model:
```python
{{request.session.expe_data|get_value_from_dict:'image_path'}}
```

For a use of html templates, the user can redirect to the official django documentation: [uses of html templates](https://docs.djangoproject.com/en/3.2/topics/templates/).

### 5. Data access and management using Javascript and Django

The access and exchange of data between Javascript and Django is not the most obvious. We will present here the tricks used to allow the exchange of client/server data.


#### 5.1. Access Django variables from Javascript:
```javascript
// EXPE variables parts
// get access to Django variables (from session)
var BEGIN_EXPE = "{{request.session.expe_started}}" === 'True'
var END_EXPE   = "{{request.session.expe_finished}}" === 'True'

// get current id from session if exists
var currentId = "{{request.session.id}}"

// List of experiments (current state request)
var expes = "{{expes_names}}"
```

#### 5.2. Update Django session from Javascript:

The Javascript session and the Django session are two different data states. It is not possible to update a variable in the Django session directly from Javascript. It is necessary to create an intermediate request.

An intermediate route has been created to retrieve the data sent by the client (Javascript) and update the Django session.
```python
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
```

The configuration of this route is specified in the `expe/expes/urls.py` file.

The javascript file `static/js/updateData.js` provides the `updateSession` function which allows this route to be called and the desired data and key stored in session.

```javascript
function updateSession(route, key, value){

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const updateUrl = `/${route}`

    return fetch(updateUrl, {
        method: 'POST',
        body: `key=${key}&value=${value}`,
        headers: {
            'Content-type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        }
    })
}
```

**Note: the required CSRF token is automatically added to the Django template `base.html`.

It is therefore possible to retrieve and update the session from javascript. Here is an example of updating the response time obtained from the client after the user's keyboard interaction:

```javascript

// Start of experiment iteration (content loaded and stimilu displayed)
var startAnswerTime = Date.now()

// Do some stuff to catch user interaction
...

// Get answer time
let answerTime = Date.now() - startAnswerTime

// Update session with answer time and then redirect
updateSession('update_session_user', 'expe_answer_time', answerTime)
.then(_ => {
    // Do whatever you want after answer update
    ...
})
```

It is now possible to get access to the variable stored in the session on the Django side:

```python
answer_time = request.session['expe_answer_time']
```

**Note**: an example of updating the user response time with captured keyboard interactions is available in the scripts: 
- `static/js/loadImg.js`: waits for the stimulus displayed to the user and initializes the starting response time;
- `static/js/keyEvents.js`: captures the keyboard interaction and sends the response time.
