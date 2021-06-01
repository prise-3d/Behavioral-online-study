
// Download endpoint response as a file using a POST request
function updateSession(route, value){

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const updateUrl = `/${route}`

    fetch(updateUrl, {
        method: 'POST',
        body: `value=${value}`,
        headers: {
            'Content-type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        }
    }).then(async res => {
        console.log('success udpate')
    })
}

function updateExpeData() {

    // access storage
    const localStorage = window.localStorage;
    
    if (expes !== undefined && !localStorage.getItem('p3d-user-id')) {

        var finalJson = {}

        var expes_corrected = expes.toString('utf8').replace(/\&quot;/g, '"' )
        var expes_json = JSON.parse(expes_corrected)    

        for(var expe in expes_json) {

            // contruct object
            expe_name = expes_json[expe]
            finalJson[expe_name] = {'done': false}
        }

        localStorage.setItem('p3d-user-expes', JSON.stringify(finalJson))

         // update data into request.session object
        updateSession('update_session_user_expes', JSON.stringify(finalJson))
    }
}

function updateId() {

    // now store into session data information
    if(localStorage.getItem('p3d-user-id')){
        
        // update data into request.session object
        updateSession('update_session_user_id', localStorage.getItem('p3d-user-id'))
    }

}

function updateData() {

    const localStorage = window.localStorage;

    // now check if new user, then add session id into local storage, if new id is generated
    if(!localStorage.getItem('p3d-user-id') && currentId){
        
        localStorage.setItem('p3d-user-id', currentId)
    }

    console.log('END expe', END_EXPE)

    if(END_EXPE){

        console.log('Update user data for')
        console.log('expe ', expeName)
        console.log('--------------------')

        // update storage data
        var user_expes = JSON.parse(localStorage.getItem('p3d-user-expes'))

        // set scene of expe has done for current user
        user_expes[expeName]['done'] = true

        // update data into request.session object and local storage
        localStorage.setItem('p3d-user-expes', JSON.stringify(user_expes))
        updateSession('update_session_user_expes', JSON.stringify(user_expes))
    }
}

window.addEventListener('DOMContentLoaded', () => {
    updateId()
    updateExpeData()
    updateData()
})