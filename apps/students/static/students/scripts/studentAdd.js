const studentAddForm = document.querySelector("#student-add-form");
const studentAddFormCard = studentAddForm.parentElement;
const studentAddButton = studentAddForm.querySelector('button[type="submit"]');
const studentAddFormToggleButton = document.querySelector("#add-student-btn");

addOnPostAndOnResponseFuncAttr(studentAddButton, 'Hold on...');


studentAddFormToggleButton.addEventListener("click", () => {
    formCards.forEach((card) => {
        if (card != studentAddFormCard) {
            card.classList.remove("show-block");
        }
    });
    
    studentAddFormCard.classList.toggle("show-block");
});


studentAddForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    studentAddButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }
    
    fetch(this.action, options).then((response) => {
        if (!response.ok) {
            studentAddButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    console.log(errors)
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        if (fieldName == "__all__"){
                            if (typeof msg === Array){
                                msg.forEach((m) => {
                                    pushNotification("error", m);
                                });
                            }else{
                                pushNotification("error", msg);
                            };
                        };
                        
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        if (!field) return;
                        field.scrollIntoView({"block": "center"});
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? data.message ?? 'An error occurred!');
                };
            });

        }else{
            studentAddButton.onResponse();
            studentAddButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? data.message ?? 'Request successful!');

                const redirectURL  = data.redirect_url ?? null
                if(!redirectURL) return;

                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);
            });
        }
    }).catch((error) => {
        studentAddButton.onResponse();
        pushNotification("error", error ?? 'An error occurred!');
    });
};

