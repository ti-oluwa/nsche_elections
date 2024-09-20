const votingForms = document.querySelectorAll('.voting-form');


votingForms.forEach(votingForm => {
    const votingFormButton = votingForm.querySelector('.submit-btn');

    addOnPostAndOnResponseFuncAttr(votingFormButton, 'Registering vote...');

    votingForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
        

        const formData = new FormData(votingForm);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        votingFormButton.onPost();
    
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify(data),
        }
    
        fetch(votingForm.action, options).then((response) => {
            votingFormButton.onResponse();
    
            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if(errors){
                        if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")
    
                        for (const [fieldName, msg] of Object.entries(errors)){
                            let field = votingForm.querySelector(`input[name=${fieldName}]`);
                            if(!field){
                                pushNotification("error", msg);
                                continue;
                            }
                            formFieldHasError(field.parentElement, msg);
                        };
    
                    }else{
                        pushNotification("error", data.detail ?? 'An error occurred!');
                    }
                });
                
            }else{
                response.json().then((data) => {
                    pushNotification("success", data.detail ?? 'Vote registered successfully!');

                    const redirectURL = data.redirect_url ?? null;
                    if (!redirectURL) return;

                    setTimeout(() => {
                        window.location.href = redirectURL;
                    }, 2000);
                });
            }
        }).catch((error) => {
            votingFormButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    }
});
