const delay = ms => new Promise(res => setTimeout(res, ms))

window.addEventListener('DOMContentLoaded', async () => {
    
    // only if not end of expe
    if (!END_EXPE) {
        var imgBlock = document.getElementById('expeImg')
        // await delay(500)
        imgBlock.onload = function() {
            console.log('Image now loaded')
            document.getElementById('expeImg').style.display = 'inline'
        }
    }
})
