const studentsImportForm = document.querySelector("#students-import-form");
const studentsImportFormCard = studentsImportForm.parentElement;
const studentsImportButton = studentsImportForm.querySelector('button[type="submit"]');
const studentsImportFormToggleButton = document.querySelector("#import-students-btn");

addOnPostAndOnResponseFuncAttr(studentsImportButton, 'Importing details...');


studentsImportFormToggleButton.addEventListener("click", () => {
    formCards.forEach((card) => {
        if (card != studentsImportFormCard) {
            card.classList.remove("show-block");
        }
    });

    studentsImportFormCard.classList.toggle("show-block");
});


studentsImportForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);

    studentsImportButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: formData,
    }
    
    fetch(this.action, options).then((response) => {
        if (!response.ok) {
            studentsImportButton.onResponse();
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
            studentsImportButton.onResponse();
            studentsImportButton.disabled = true;

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
        studentsImportButton.onResponse();
        pushNotification("error", error ?? 'An error occurred!');
    });
};

