// KEY event codes
const KEYCODE_LEFT_ARROW  = 37
const KEYCODE_RIGHT_ARROW = 39

// check if keyboard already pressed for specific key events
var keyUsed = false;

// store when answer can begin
var start_answer_time = null;

// Function which check key event
const checkKey = e => {

    // check specific keys
    if ((e.keyCode === KEYCODE_LEFT_ARROW || e.keyCode === KEYCODE_RIGHT_ARROW) && !keyUsed) {

        // track only first answer event
        keyUsed = true;

        // 0 if left arrow event otherwise 1
        let answer_value = 0 ? e.keyCode === KEYCODE_LEFT_ARROW : 1

        // Get answer time 
        let answer_time = Date.now() - start_answer_time;

        // Do whatever you want
        quest_form = document.querySelector('form[class="quest-form"]');

        // set specific input values
        document.querySelector('input[name="quest-answer-time"]').value = answer_time
        document.querySelector('input[name="quest-answer-value"]').value = answer_value
        
        // then submit form
        quest_form.submit();
   }
}

// Example of Javascript use for example page
document.addEventListener('DOMContentLoaded',() => {

    // load images
    var start_answer_time = null;
    var experiment_images = document.querySelectorAll('img[class="quest-experiment-image"]')
    

    if (experiment_images !== null) {
        experiment_images.forEach(e => { 
            e.style.display = 'inline'
        });
    }

    // Once images are loaded, the stimulus is then available we can measure the answer time
    start_answer_time = Date.now();

    // implement `key` events when document loaded
    document.addEventListener('keydown', checkKey)
});

