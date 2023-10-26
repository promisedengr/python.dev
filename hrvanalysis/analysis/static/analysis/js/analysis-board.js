setSampleForm();
setResultForm();
validSettingsForm();
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



let form = document.getElementById('updateSampleForm');
form.addEventListener('submit', e => {
    e.preventDefault()
    let url = document.getElementById('apiUpdateSampleEndPoint').href;
    document.querySelector('body').classList.remove("loaded");
    const comment = document.getElementById('sampleComment').value
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            "comment": comment
        })
    }).then(function (resp) {
        document.querySelector('body').classList.add("loaded");
        let commentPara = document.getElementById('commentText');
        commentPara.innerText = comment;
        // let alert = document.createElement('div');
        // alert.setAttribute('class', 'alert alert-info alert-dismissible show fade mx-5');
        // alert.setAttribute('role', 'alert');
        // alert.innerHTML = `
        // Comment updated
        // <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        //     <span aria-hidden="true">&times;</span>
        // </button>        
        // `
        // document.getElementById('alertMsg').appendChild(alert);
    }).catch((error) => {
        document.querySelector('body').classList.add("loaded");
        console.error('Error:', error);
        let alert = document.createElement('div');
        alert.setAttribute('class', 'alert alert-danger alert-dismissible show fade mx-5');
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
        Something went wrong when updating
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>        
        `
        document.getElementById('alertMsg').appendChild(alert);
    });

})



let resultForm = document.getElementById('updateResultForm');
resultForm.addEventListener('submit', e => {
    e.preventDefault()
    if (validSettingsForm()) {
        let url = document.getElementById('apiUpdateResultEndPoint').href;        
        document.querySelector('body').classList.remove("loaded");

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                "settings": {
                    "kwargs_time": {
                        "threshold": parseInt(document.getElementById('id_threshold').value) ?? 10,
                        "binsize": parseFloat(document.getElementById('id_binsize').value) ?? 7.8125,
                    },
                    "interval": [parseInt(document.getElementById('id_interval_lower').value) ?? 0, parseInt(document.getElementById('id_interval_upper').value) ?? 10],
                    "kwargs_tachogram": {
                        'title': document.getElementById('id_tachogram_title').value ?? 'tachogram',
                        'hr': document.getElementById('id_tachogram_hr').checked ?? true
                    },
                }
            })
        }).then(function (resp) {
            document.querySelector('body').classList.add("loaded");
            // let alert = document.createElement('div');
            // alert.setAttribute('class', 'alert alert-info alert-dismissible show fade mx-5');
            // alert.setAttribute('role', 'alert');
            // alert.innerHTML = `
            // Result updated
            // <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            //     <span aria-hidden="true">&times;</span>
            // </button>        
            // `
            // document.getElementById('alertMsg').appendChild(alert);
            return resp.json();
        }).then(function (data) {
            let tachogram = document.getElementById('tachogram-chart')
            tachogram.innerHTML = data.tachogram_plot
            let nn_histogram = document.getElementById('nn_histogram-chart')
            nn_histogram.innerHTML = data.nn_histogram
            let lomb = document.getElementById('lomb-chart')
            lomb.innerHTML = data.lomb_plot
            let fft = document.getElementById('fft-chart')
            fft.innerHTML = data.fft_plot
            let poincare = document.getElementById('poincare-chart')
            poincare.innerHTML = data.poincare_plot
            let dfa = document.getElementById('dfa-chart')
            dfa.innerHTML = data.dfa_plot
        }).catch((error) => {
            document.querySelector('body').classList.add("loaded");
            console.error('Error:', error);
            let alert = document.createElement('div');
            alert.setAttribute('class', 'alert alert-danger alert-dismissible show fade mx-5');
            alert.setAttribute('role', 'alert');
            alert.innerHTML = `
            Something went wrong when updating
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>        
            `
            document.getElementById('alertMsg').appendChild(alert);
        });
    }
})

// Return an array of the selected opion values
// select is an HTML select element
function getSelectValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i = 0, iLen = options.length; i < iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            result.push(opt.value ?? opt.text);
        }
    }
    return result;
}

let compareForm = document.getElementById('compareSampleForm');
compareForm.addEventListener('submit', e => {
    e.preventDefault();
    document.querySelector('body').classList.remove("loaded");
    let url = document.getElementById('apiUpdateResultEndPoint').href;
    let sample_id = document.getElementById('selectSample').value;
    let parameters = getSelectValues(document.getElementById('comparisonParams'));
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            "radar_chart_params": {
                "sample_id": parseInt(sample_id),
                "parameters": parameters
            }
        })

    }).then(resp => {
        document.querySelector('body').classList.add("loaded");
        return resp.json();
    }).then(function (data) {
        let radar = document.getElementById('radar-chart')
        radar.innerHTML = data.radar_plot
    }).catch((error) => {
        console.error('Error:', error);
        let alert = document.createElement('div');
        alert.setAttribute('class', 'alert alert-warning alert-dismissible show fade mx-5');
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
        Something went wrong when trying to compare
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>        
        `
        document.getElementById('alertMsg').appendChild(alert);
    });
})

function setSampleForm() {
    let url = document.getElementById('apiUpdateSampleEndPoint').href;
    let comment = document.getElementById('sampleComment')
    fetch(url).then(resp => resp.json()).then(function (data) {
        comment.value = data.comment
    })
}

function setResultForm() {
    let url = document.getElementById('apiUpdateResultEndPoint').href;
    let threshold = document.getElementById('id_threshold')
    let binsize = document.getElementById('id_binsize')
    let title = document.getElementById('id_tachogram_title')
    let hr = document.getElementById('id_tachogram_hr')
    let interval_lower = document.getElementById('id_interval_lower')
    let interval_upper = document.getElementById('id_interval_upper')
    fetch(url).then(resp => resp.json()).then(function (data) {
        if (data.settings != null) {
            try {
                threshold.value = data.settings.kwargs_time.threshold
            } catch (e) { }

            try {
                title.value = data.settings.kwargs_tachogram.title
            } catch (e) { title.value = "tachogram" }

            try {
                hr.checked = data.settings.kwargs_tachogram.hr
            } catch (e) { hr.checked = true }

            try {
                interval_lower.value = data.settings.interval[0]
            } catch (e) { interval_lower.value = 0 }

            try {
                interval_upper.value = data.settings.interval[1]
            } catch (e) { interval_upper.value = 10 }

            try {
                binsize.value = data.settings.kwargs_time.binsize
            } catch (e) { binsize.value = 7.8125 }

        } else {
            title.value = "tachogram"
            hr.checked = true
            interval_lower.value = 0
            interval_upper.value = 10
            binsize.value = 7.8125
        }


    })

}



function validSettingsForm() {
    let threshold = document.getElementById('id_threshold');
    let invalid_threshold = document.createElement('div');
    invalid_threshold.innerHTML = "<small>Please provide a positive number.</small>";
    invalid_threshold.setAttribute("class", "text-danger font-weight-bold d-none");
    document.querySelector('#div_id_threshold > div:nth-child(2)').appendChild(invalid_threshold);
    threshold.addEventListener('input', () => {
        if (threshold.value < 0) {
            threshold.classList.add("is-invalid");
            invalid_threshold.classList.remove("d-none");
        } else {
            threshold.classList.remove("is-invalid");
            invalid_threshold.classList.add("d-none");
        }
    })

    let binsize = document.getElementById('id_binsize');
    let invalid_binsize = document.createElement('div');
    invalid_binsize.innerHTML = "<small>Please provide a positive size.</small>";
    invalid_binsize.setAttribute("class", "text-danger font-weight-bold d-none");
    document.querySelector('#div_id_binsize > div:nth-child(2)').appendChild(invalid_binsize);
    binsize.addEventListener('input', () => {
        if (binsize.value < 0) {
            binsize.classList.add("is-invalid");
            invalid_binsize.classList.remove("d-none");
        } else {
            binsize.classList.remove("is-invalid");
            invalid_binsize.classList.add("d-none");
        }
    })
    let interval_lower = document.getElementById('id_interval_lower');
    let invalid_interval_lower = document.createElement('div');
    invalid_interval_lower.innerHTML = "<small>Please provide a valid positive bound.</small>";
    invalid_interval_lower.setAttribute("class", "text-danger font-weight-bold d-none");
    document.querySelector('#div_id_interval_lower > div').appendChild(invalid_interval_lower);
    interval_lower.addEventListener('input', () => {
        if (interval_lower.value < 0 || interval_upper.value < interval_lower.value) {
            interval_lower.classList.add("is-invalid");
            invalid_interval_lower.classList.remove("d-none");
        } else {
            interval_lower.classList.remove("is-invalid");
            invalid_interval_lower.classList.add("d-none");
        }
    })
    let interval_upper = document.getElementById('id_interval_upper');
    let invalid_interval_upper = document.createElement('div');
    invalid_interval_upper.innerHTML = "<small>Invalid upper bound.</small>";
    invalid_interval_upper.setAttribute("class", "text-danger font-weight-bold d-none");
    document.querySelector('#div_id_interval_upper > div').appendChild(invalid_interval_upper);
    interval_upper.addEventListener('input', () => {
        if (interval_upper.value < 0 || interval_upper.value < interval_lower.value) {
            interval_upper.classList.add("is-invalid");
            invalid_interval_upper.classList.remove("d-none");
        } else {
            interval_upper.classList.remove("is-invalid");
            invalid_interval_upper.classList.add("d-none");
        }
    })
    if (threshold.value < 0 || binsize.value < 0 || interval_lower.value < 0 || interval_upper.value < 0 || interval_upper.value < interval_lower.value) return false
    return (true)

}
