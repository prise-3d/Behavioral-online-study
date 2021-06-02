const delay = ms => new Promise(res => setTimeout(res, ms))

window.addEventListener('DOMContentLoaded', async () => {
    
    // only if not end of expe
    if (!END_EXPE) {
        var imgBlock = document.getElementById('expeImg')
        
        imgBlock.onload = function() {
            document.getElementById('expeImg').style.display = 'inline'
        }
    }
})
