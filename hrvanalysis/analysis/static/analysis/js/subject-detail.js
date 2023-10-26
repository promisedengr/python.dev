uploadFiles();

function uploadFiles() {
    let uploadcard = document.getElementById('uploadFile');
    uploadcard.addEventListener('click', () => {
        let fileUploads = document.getElementById('selectFiles');
        fileUploads.className = fileUploads.className.replace(/\bd-none\b/g, "");
    })
    let signalInput = document.getElementById('inputFileSignal');
    let nniInput = document.getElementById('inputNNIfile');
    signalInput.addEventListener('change', () => {
        document.getElementById("nniData").className = 'd-none';
        document.getElementById("submitfilebtn").classList.remove("d-none");
    })
    nniInput.addEventListener('change', () => {
        document.getElementById("signalData").className = 'd-none';
        document.getElementById("submitfilebtn").classList.remove("d-none");
    })

    document.getElementById('btnFileSubmit').addEventListener('click', ()=>{
        document.querySelector('body').classList.remove("loaded");
    })

}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


var getClosest = function (elem, selector) {

    // Element.matches() polyfill
    if (!Element.prototype.matches) {
        Element.prototype.matches =
            Element.prototype.matchesSelector ||
            Element.prototype.mozMatchesSelector ||
            Element.prototype.msMatchesSelector ||
            Element.prototype.oMatchesSelector ||
            Element.prototype.webkitMatchesSelector ||
            function (s) {
                var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                    i = matches.length;
                while (--i >= 0 && matches.item(i) !== this) { }
                return i > -1;
            };
    }

    // Get the closest matching element
    for (; elem && elem !== document; elem = elem.parentNode) {
        if (elem.matches(selector)) return elem;
    }
    return null;

};

const deleteForms = document.getElementsByClassName('deleteSampleForm');

for (const form of deleteForms) {
    form.addEventListener('submit', e => {
        e.preventDefault();
        let url = form.id
        fetch(url, {
            'method': 'DELETE',
            'headers': {
                'Content-type': 'application/json',
                'X-CSRFToken': csrftoken,
            }
        }).then(resp => {
            let card = getClosest(form, '.sampleCard');
            card.remove();
        })
    })
}


// filter samples
document.getElementById("filterSample").addEventListener('keyup', () => {
    let input = document.getElementById("filterSample");
    let filter = input.value.toUpperCase();
    let wrapper = document.getElementById('sample-wrapper');
    let cards = wrapper.getElementsByClassName('sampleCard');
    for (i = 0; i < cards.length; i++) {
        let h2 = cards[i].getElementsByTagName("h2")[0];
         
        let txtValue = h2.textContent || h2.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }    
})
