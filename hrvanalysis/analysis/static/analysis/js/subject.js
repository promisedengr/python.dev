subjectList();

// initialize the scrollbar
if (typeof PerfectScrollbar == 'function') {
    let container = document.querySelector("#subject-container");
    let ps = new PerfectScrollbar(container);
}

// global variable to know whether the subject is  being edited or created
let activeSubject = null;

function subjectList() {
    let url = document.getElementById('apiCreateEndPoint').href;    
    let container = document.getElementById('subject-container')
    container.innerHTML = '';

    fetch(url).then((resp) => resp.json()).then(function (data) {
        let list = data;
        list.forEach(element => {
            let subject = `
                    <div class="col-md-6 col-12">
                        <div class="card text-center">
                            <div class="card-body">
                                <h4 class="card-title">${element.name}</h4>
                                <a class="btn btn-outline-primary btn-block mb-2" href="/subjects/${element.id}/samples/"> Go to samples</a>
                                <p>Gender: ${element.gender}
                                <br>Age: ${element.age}</p>
                                <div class="row">
                                    <div class="col-lg-6 col-12 mb-2"><button class="btn btn-secondary btn-block edit">Edit</button></div>
                                    <div class="col-lg-6 col-12 mb-2"><button class="btn btn-primary btn-block delete">Delete</button></div>
                                </div>
                            </div>
                        </div>
                    </div>           
            `
            container.innerHTML += subject
        });


        for (let i in list) {
            let editBtn = document.getElementsByClassName('edit')[i];
            let deleteBtn = document.getElementsByClassName('delete')[i];

            editBtn.addEventListener('click', (function (subject) {
                return function () {
                    editSubject(subject)
                }
            })(list[i]))

            deleteBtn.addEventListener('click', (function (subject) {
                return function () {
                    deleteSubject(subject)
                }
            })(list[i]))
        }

        let addSubjectMsg = document.createElement('p')
        
        addSubjectMsg.innerText = "Please fill in your study subjects information"
        addSubjectMsg.setAttribute('class','lead text-center')
            
        if(list.length == 0) {
            container.setAttribute('class','d-flex align-items-center')
            container.appendChild(addSubjectMsg)
        }
        container.setAttribute('class','row')       

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


function validateForm() {
    let name = document.getElementById('subjet-name-id').value;
    let gender = document.getElementById('subjet-gender-id').value;
    let age = document.getElementById('subjet-age-id').value;
    if (name == "") {
        let invalidmsg = document.createElement('div')
        invalidmsg.innerHTML = "Please provide the subject's name.";
        invalidmsg.classList.add("invalid-feedback");
        document.getElementById('subjet-name').appendChild(invalidmsg);
        return false;
    }
    if (gender == "") {
        let invalidmsg = document.createElement('div')
        invalidmsg.innerHTML = "Please provide the subject's gender.";
        invalidmsg.classList.add("invalid-feedback");
        document.getElementById('subjet-gender').appendChild(invalidmsg);
        return false;
    }
    if (isNaN(age) || age < 1) {
        let invalidmsg = document.createElement('div')
        invalidmsg.innerHTML = "Please provide a valid age.";
        invalidmsg.classList.add("invalid-feedback");
        document.getElementById('subjet-age').appendChild(invalidmsg);
        return false;
    }
    return (true);
}


let form = document.getElementById('addSubjectForm');
form.addEventListener('submit', e => {
    e.preventDefault();
    if (validateForm() == true) {
        let url = document.getElementById('apiCreateEndPoint').href;
        let method = 'POST';
        if (activeSubject != null) {
            url = activeSubject.url;
            method = 'PATCH'
            activeSubject = null;
        }

        let name = document.getElementById('subjet-name-id').value;
        let gender = document.getElementById('subjet-gender-id').value;
        let age = parseInt(document.getElementById('subjet-age-id').value);
        fetch(url, {
            method: method,
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(
                {
                    "name": name,
                    "gender": gender,
                    "age": age
                }
                )
        }).then(function (resp) {
            subjectList();
            document.getElementById('addSubjectForm').reset();
            // let alert = document.createElement('div');
            // alert.setAttribute('class', 'alert alert-info alert-dismissible show fade mx-5');
            // alert.setAttribute('role', 'alert');
            // if (method == 'POST') {
            // alert.innerHTML = `
            // Subject added successfully
            // <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            //     <span aria-hidden="true">&times;</span>
            // </button>        
            // `
            // } else {
            //     alert.innerHTML = `
            //     Subject was updated
            //     <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            //         <span aria-hidden="true">&times;</span>
            //     </button>        
            //     `                
            // }

            // document.getElementById('alertMsg').appendChild(alert);
        }).catch((error) => {
            console.error('Error:', error);
            let alert = document.createElement('div');
            alert.setAttribute('class', 'alert alert-danger alert-dismissible show fade mx-5');
            alert.setAttribute('role', 'alert');
            alert.innerHTML = `
            Something went wrong, We could not perform the action
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>        
            `
            document.getElementById('alertMsg').appendChild(alert);
        });
    }
    else {
        console.log('form is invalid');
    }

})


function editSubject(subject) {
    activeSubject = subject
    document.getElementById('subjet-name-id').value = activeSubject.name;
    document.getElementById('subjet-gender-id').value = activeSubject.gender;
    document.getElementById('subjet-age-id').value = activeSubject.age;
    document.documentElement.scrollTo({
        top: 0,
        behavior: "smooth"
      })
}


function deleteSubject(subject) {
    url = subject.url
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    }).then(resp => subjectList()).catch((error) => {
        console.error('Error:', error);
        let alert = document.createElement('div');
        alert.setAttribute('class', 'alert alert-danger alert-dismissible show fade mx-5');
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
        Something went wrong, We could not delete this subject
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>        
        `
        document.getElementById('alertMsg').appendChild(alert);
    });
}