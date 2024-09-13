const detailVerificationForm = document.querySelector('#detail-verification-form');
const detailVerificationButton = detailVerificationForm.querySelector('.submit-btn');
const emailField = detailVerificationForm.querySelector('#email');

const OTPVerificationForm = document.querySelector("#otp-verification-form");
const OTPVerificationButton = OTPVerificationForm.querySelector(".submit-btn");

const registrationCompletionForm = document.querySelector("#registration-completion-form");
const passwordField1 = registrationCompletionForm.querySelector('#password');
const passwordField2 = registrationCompletionForm.querySelector('#confirm_password');
const registrationCompletionButton = registrationCompletionForm.querySelector(".submit-btn");


addOnPostAndOnResponseFuncAttr(detailVerificationButton, 'Verifying...');
addOnPostAndOnResponseFuncAttr(OTPVerificationButton, 'Verifying OTP...');
addOnPostAndOnResponseFuncAttr(registrationCompletionButton, 'Please wait...');


function showFormCardOnly(formCard){
    formCards.forEach(card => {
        if (card == formCard){
            card.classList.add("show-block");
        } else {
            card.classList.remove("show-block");
        }
    });
};

function showRegistrationCompletionForm(completionData) {
    registrationCompletionForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
        
        if (!validatePassword(passwordField1, passwordField2)) return;

        const formData = new FormData(registrationCompletionForm);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            payload[key] = value;
        }
    
        registrationCompletionButton.onPost();
    
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify({...payload, ...completionData}),
        }
    
        fetch(registrationCompletionForm.action, options).then((response) => {
            registrationCompletionButton.onResponse();
    
            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if(errors){
                        if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")
    
                        for (const [fieldName, msg] of Object.entries(errors)){
                            let field = registrationCompletionForm.querySelector(`input[name=${fieldName}]`);
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
                    pushNotification("success", data.detail ?? 'Registration completed successful!');

                    const redirectURL = data.redirect_url ?? null;
                    if (!redirectURL) return;

                    setTimeout(() => {
                        window.location.href = redirectURL;
                    }, 2000);
                });
            }
        }).catch((error) => {
            registrationCompletionButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(registrationCompletionForm.parentElement);
}


function showOTPVerificationForm(studentData) {
    OTPVerificationForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
        
        const formData = new FormData(OTPVerificationForm);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            payload[key] = value;
        }
    
        OTPVerificationButton.onPost();
    
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify({...payload, ...studentData}),
        }
    
        fetch(OTPVerificationForm.action, options).then((response) => {
            OTPVerificationButton.onResponse();
    
            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if(errors){
                        if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")
    
                        for (const [fieldName, msg] of Object.entries(errors)){
                            let field = OTPVerificationForm.querySelector(`input[name=${fieldName}]`);
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
                    pushNotification("success", data.detail ?? 'OTP verified successfully!');
                    OTPVerificationForm.reset();

                    const responseData = data.data ?? null;
                    if (!responseData) return;

                    showRegistrationCompletionForm(responseData)
                });
            }
        }).catch((error) => {
            OTPVerificationButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(OTPVerificationForm.parentElement);  
}


detailVerificationForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    
    const formData = new FormData(detailVerificationForm);
    const payload = {};
    for (const [key, value] of formData.entries()) {
        payload[key] = value;
    }

    detailVerificationButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(payload),
    }

    fetch(detailVerificationForm.action, options).then((response) => {
        detailVerificationButton.onResponse();

        if (!response.ok) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;
                
                if(errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = detailVerificationForm.querySelector(`input[name=${fieldName}]`);
                        if(!field){
                            pushNotification("error", msg);
                            continue;
                        }
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? 'An error occurred!');
                }

                if (!redirectURL) return;
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 2000);
            });
            
        }else{
            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Verification successful!');
                detailVerificationForm.reset();
                showOTPVerificationForm(payload);
            });
        }
    }).catch((error) => {
        detailVerificationButton.onResponse();
        pushNotification("error", error ?? 'An error occurred!');
    });
};


