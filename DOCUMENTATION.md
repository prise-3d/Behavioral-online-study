# Documentation and tutorial (create your own experiment)

## Description

This website can let you create and manage your own experiments using Python as backend. 

Why such application ? A lot of experimental development are done in Python, you can quickly include it and create your experiments.

For a better understanding of this documentation, the user is invited to take a minimal knowledge of the use of the Django framework: [django documentation](https://docs.djangoproject.com/en/3.2/).

## Explanations

The `expe` module is the django app created for managing experiments.

Main app folders:
- `expe/config.py`: contains the main variables used by website, save experiments content and experiments configuration;
- `expe/views.py`: is django app file used for enable routes of website;
- `expe/expes/run.py`: contains **run_{expe_name}** functions in order to launch dynamically step of experiments;
- `expe/expes/classes`: is folder which contains all the necessary Python classes for experiments;
- `expe/expes/templates`: is folder which contains all `.html` template with Django scripting variables displayed;
- `expe/expes/urls.py`: bind the url routes with `views.py` functions (POST or GET methods).

Other folders:
- `static`: contains `css`, `js` and usefull static resources for website such as images;
- `media`: generated experiment files such as log file, saved model Quest+ state binary file when users pass experiments.

**Note**: We will discuss in more detail the subtleties of using javascript and Django request and session variables.

## Create your own experiments

### 1. Experience configuration

Let's start with the `expe/config.py` python file. As explained earlier, this file contains experiments configuration. The variable `expes_configuration` is the dictionnary which declares all information of experiments.

An overview of the `quest_example` key experiment configuration:

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

    # if others custom session param are directly set for experiments
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

The `params` section is where you put all your necessary information for your experiments.

### 2. The experiments `expe` route

The `expe/` route define by the `expe` function in `expe/views.py` is used for launching experiments. This route uses few parameters pass using `GET` method:
- `expe`: the current experiment name to use
- `iteration`: step of this experiments
- `answer`: the answer of the user

Using this parameter, the route know which experiments to launch with specific scene and manage experiments steps.

**Note:** `answer` and `iteration` parameters are used into `js/keyEvents.js` file. This means the `answer` and `iteration` values are sent depending of user interactions. You can implement your own interaction by creating your own `js` file and add it into your experiments configuration declaration (see `expe/config.py`).

### 3. The `run` experiments function

Into the `expe` function in `expe/views.py`, the `run` method of your experiment is dynamically call based. Hence you need to implement into the `expe/expes/run.py` a function which follows this naming convention:

- `run_{your_experiment_name}`

You have communication exchanges between the Django server and the client side, it's necessary to store the experiments process at each step.

Hence, this function need to follow this prototype:

```python
def run_{your_experiment_name}(request, model_filepath, output_file):
```

Information about parameters:
- `request`: contains all information into `GET`, `POST` and session storages
- `model_filepath`: filename where you need to store information about experiment model (such as Quest+ or whatever you want) into a binary file (can be just data information or object instanciated from file of `expe/expes/classes`)
- `output_file`: buffer where you can add information about your experiments (following your `output_header` declared into your experiment configuration into `expe/config.py`)


Example of accessing request variables:
```python
expe_name_session = request.session.get('expe')
expe_name_get     = request.GET.get('expe')
expe_name_post    = request.POST.get('expe')
```

Example of loading or saving Python Quest+ object ([pickle](https://docs.python.org/3/library/pickle.html) serialization library is required):
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

### 4. Display experiments data into custom template

Finally your `run` function need to return python dictionnary of **data** your need to use into your `expe/` django template. 

Several types of information can be accessed from the Django template, it is important to differentiate it:

- **Request data:** the set of data (dictionnary) sent from the request when choosing the rendered template;
- **Session**: for information related more to the context of the experiment and not only the current request, it is possible to store data in the session. In this way, within the template, it is possible to retrieve, display and process the user's session data. 


If you want to create your own template, specify your template path into configuration:
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

Example of way to use your experiments current request data with safe display (html encoding) into template:
```python
{{end_text | safe}}
```

Example of way to use your experiment session data and access specific dictionary key into template:
```python
{{request.session.expe_data|get_value_from_dict:'image_path'}}
```

For a use of the templates the user can redirect to the official documentation of django: [template usages](https://docs.djangoproject.com/en/3.2/topics/templates/).

### 5. Data access and management using Javascript and Django

The access and exchange of data between Javascript and Django is not the most obvious. We will present here the tricks used to allow the exchange of client / server data.


#### 5.1. Access Django variable from Javascript:
```javascript
// EXPE variables parts
// get access to django variables (from session)
var BEGIN_EXPE = "{{request.session.expe_started}}" === 'True'
var END_EXPE   = "{{request.session.expe_finished}}" === 'True'

// get current id from session if exists
var currentId = "{{request.session.id}}"

// List of experiments (current state request)
var expes = "{{expes_names}}"
```

#### 5.2. Update Django session from Javascript:

The Javascript session and the Django session are both different data state. It is not directly possible to update a variable in Django session from Javascript. It is necessary to create an intermediate request.


An intermediate route has been created to retrieve data sent from the client (Javascript) and update the Django session.
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

The configuration of this route is specified in the file `expe/expes/urls.py`.

The javascript file `static/js/updateData.js` proposes the function `updateSession` which allows the call to this route and to store the desired data and key in session.

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

**Note**: the required CSRF token is added automatically in the `base.html` Django template.

It is thus possible to retrieve and update the session from javascript. Here is an example of updating the response time obtained from the client after the user's keyboard interaction:

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

It is now possible to retrieve the access to the variable stored in session on Django side:
```python
answer_time = request.session['expe_answer_time']
```

**Note**: an example of user response time update with keyboard interaction capture is available in the scripts: 
- `static/js/loadImg.js`: wait for stimulus displayed to user and initialize the start answer time;
- `static/js/keyEvents.js`: keyboard interaction capture and answer time sent.
