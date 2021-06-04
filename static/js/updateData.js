
// Download endpoint response as a file using a POST request
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


function getData() {

    // Get client id if exists into local storage (client part)
    // Now store into session previous data information, here the client ID
    if(localStorage.getItem('p3d-user-id')){
        
        // update data into request.session object
        updateSession('update_session_user', 'id', localStorage.getItem('p3d-user-id'))
            .then('User id updated')
    }

    // TODO : here you can update into session anything you want from client session to server
    // You need to use the `update_session_user_expes` route
    // Example : updateSession('update_session_user_expes', localStorage.getItem('p3d-user-data'))
}

function updateData() {

    const localStorage = window.localStorage;

    // now check if new user, then add session id into local storage, if new id is generated
    if(!localStorage.getItem('p3d-user-id') && currentId){
        
        localStorage.setItem('p3d-user-id', currentId)
    }

    // TODO : here you can update into session anything you want from client session to server
    // You need to use the `update_session_user_expes` route
    // Example : 
    // localStorage.setItem('p3d-user-data', {})
    // updateSession('update_session_user_expes', localStorage.getItem('p3d-user-data'))
}

window.addEventListener('DOMContentLoaded', () => {
    getData()
    updateData()
})