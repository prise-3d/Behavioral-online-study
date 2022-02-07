document.addEventListener('DOMContentLoaded',() => {
    
    // Do whatever you want
    const localStorage = window.localStorage;
    const sessionStorage = window.sessionStorage;

    // now check if new participant, then add session id into local storage, if new id is generated
    const behavioral_participant_id = localStorage.getItem('behavioral-experiment-participant-id')

    // ask for new participant id
    if (!sessionStorage.getItem('behavioral-experiment-participant-id')) {

        getData('participant/check', 'POST', 'participant_uuid', behavioral_participant_id)
            .then(response => response.json())
            .then(data => {
                localStorage.setItem('behavioral-experiment-participant-id', data[0]['pk'])
                sessionStorage.setItem('behavioral-experiment-participant-id', data[0]['pk'])
            });
    }
});
