const toggleVisible = ele => ele.style.display = ele.style.display === 'none' ? 'block' : 'none'
const toggleClass = (ele, class1, class2) => ele.className = ele.className === class1 ? class2 : class1

// Download endpoint response as a file using a POST request
const downloadContent = path => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const downloadUrl = `/admin/download`

    return fetch(downloadUrl, {
        method: 'POST',
        body: `path=${path}`,
        headers: {
            'Content-type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        }
    }).then(async res => {
        console.log(res)
        if (res.status === 200) {
            // Try to find out the filename from the content disposition `filename` value
            const disposition = res.headers.get('Content-Disposition')
            // expe is find from django
            const filename = `${expe_name}_${disposition.split('=')[1]}`

            const blob = await res.blob()
            // use of `FileSaver.js` library
            saveAs(blob, filename)
        }
    })
}

window.addEventListener('DOMContentLoaded', () => {
    // Display list of files from day folder
    // need to parse as `Array`
    Array.from(document.getElementsByClassName('date-folder-list')).forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault()
            currentElem = event.currentTarget

            // get list element
            list = currentElem.parentElement.nextElementSibling
            
            // display or hide list elements
            toggleVisible(list)

            // toggle arrow class for display effect
            iconElem = currentElem.children[0]
            toggleClass(iconElem, 'fas fa-arrow-circle-right', 'fas fa-arrow-circle-down')
        })
    })

    // need to parse as `Array`
    Array.from(document.getElementsByClassName('download-list')).forEach(downloadElem => {
        downloadElem.addEventListener('click', event => {
            event.preventDefault()

            currentElem = event.currentTarget
            pathDownload = currentElem.getAttribute('data-download-path')

            downloadContent(pathDownload)
        })
    })
})
