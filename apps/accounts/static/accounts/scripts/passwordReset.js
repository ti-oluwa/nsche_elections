const passwordResetInitiationForm = document.querySelector('#password-reset-initiation-form');
const passwordResetInitiationButton = passwordResetInitiationForm.querySelector('.submit-btn');
const emailField = passwordResetInitiationForm.querySelector('#email');

const OTPVerificationForm = document.querySelector("#password-reset-otp-verification-form");
const OTPVerificationButton = OTPVerificationForm.querySelector(".submit-btn");

const passwordResetCompletionForm = document.querySelector("#password-reset-completion-form");
const passwordField1 = passwordResetCompletionForm.querySelector('#password');
const passwordField2 = passwordResetCompletionForm.querySelector('#confirm_password');
const passwordResetCompletionButton = passwordResetCompletionForm.querySelector(".submit-btn");


addOnPostAndOnResponseFuncAttr(passwordResetInitiationButton, 'Verifying...');
addOnPostAndOnResponseFuncAttr(OTPVerificationButton, 'Verifying OTP...');
addOnPostAndOnResponseFuncAttr(passwordResetCompletionButton, 'Please wait...');


function showFormCardOnly(formCard){
    formCards.forEach(card => {
        if (card == formCard){
            card.classList.add("show-block");
        } else {
            card.classList.remove("show-block");
        }
    });
};

function showPasswordResetCompletionForm(completionData) {
    passwordResetCompletionForm.onsubmit = (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
        
        if (!validatePassword(passwordField1, passwordField2)) return;

        const formData = new FormData(passwordResetCompletionForm);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            payload[key] = value;
        }
        
        passwordResetCompletionButton.onPost();
    
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            mode: 'same-origin',
            body: JSON.stringify({...payload, ...completionData}),
        }
    
        fetch(passwordResetCompletionForm.action, options).then((response) => {
            passwordResetCompletionButton.onResponse();
    
            if (!response.ok) {
                response.json().then((data) => {
                    const errors = data.errors ?? null;
                    if(errors){
                        if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")
    
                        for (const [fieldName, msg] of Object.entries(errors)){
                            let field = passwordResetCompletionForm.querySelector(`input[name=${fieldName}]`);
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
                    pushNotification("success", data.detail ?? 'Password reset successful!');

                    const redirectURL = data.redirect_url ?? null;
                    if (!redirectURL) return;

                    setTimeout(() => {
                        window.location.href = redirectURL;
                    }, 2000);
                });
            }
        }).catch((error) => {
            passwordResetCompletionButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(passwordResetCompletionForm.parentElement);
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

                    showPasswordResetCompletionForm(responseData)
                });
            }
        }).catch((error) => {
            OTPVerificationButton.onResponse();
            pushNotification("error", error ?? 'An error occurred!');
        });
    };

    showFormCardOnly(OTPVerificationForm.parentElement);  
}


passwordResetInitiationForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    
    const formData = new FormData(passwordResetInitiationForm);
    const payload = {};
    for (const [key, value] of formData.entries()) {
        payload[key] = value;
    }

    passwordResetInitiationButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(payload),
    }

    fetch(passwordResetInitiationForm.action, options).then((response) => {
        passwordResetInitiationButton.onResponse();

        if (!response.ok) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                const redirectURL = data.redirect_url ?? null;
                
                if(errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = passwordResetInitiationForm.querySelector(`input[name=${fieldName}]`);
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
                passwordResetInitiationForm.reset();
                showOTPVerificationForm(payload);
            });
        }
    }).catch((error) => {
        passwordResetInitiationButton.onResponse();
        pushNotification("error", error ?? 'An error occurred!');
    });
};


