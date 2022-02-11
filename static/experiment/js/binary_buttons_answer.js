// Example of Javascript use for example page
document.addEventListener('DOMContentLoaded',() => {

    var start_answer_time = null;
    var experiment_images = document.querySelectorAll('img[class="experiment-image"]')
    

    if (experiment_images !== null) {
        experiment_images.forEach(e => { 
            e.style.display = 'inline'
        });
    }

    // Once images are loaded, the stimulus is then available we can measure the answer time
    start_answer_time = Date.now();

    // Do whatever you want
    document.querySelector('form[class="binary-answer-form"]').onsubmit = (e) => {	
        
        e.preventDefault();

        // get answer from button
        let answer_value = document.activeElement['value']

        // Compute time and add it into form
        let answer_time = Date.now() - start_answer_time

        // set specific input values
        document.querySelector('input[name="binary-answer-time"]').value = answer_time
        document.querySelector('input[name="binary-answer-value"]').value = answer_value
        
        // then submit form
        form = e.target;
        form.submit();
    } 
});

