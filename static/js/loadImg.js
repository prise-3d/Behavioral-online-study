const delay = ms => new Promise(res => setTimeout(res, ms))
var startAnswerTime = undefined;

window.addEventListener('DOMContentLoaded', async () => {
    
    // only if not end of expe
    if (!END_EXPE) {
        var imgBlock = document.getElementById('expeImg')
        
        if (imgBlock !== null) {
            imgBlock.onload = function() {
                document.getElementById('expeImg').style.display = 'inline'

                // Once image is loaded, the stimulus is then available we can measure the answer time
                startAnswerTime = Date.now();
            }
        }
    }
})
