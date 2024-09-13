/**
 * Gets the element that displays messages for the form field
 * @param {Element} formField The form field
 * @returns The message element of the form field
 */
function getMsgEl(formField) {
    if (!formField.classList.contains('form-field')) {
        throw new Error('Field must have class "form-field"');
    }
    return formField.querySelector('.field-message');
};


/**
 * Sets and displays the error message for the form field
 * @param {Element} formField The form field that has an error
 * @param {string} errorMsg The error message to display
 */
function formFieldHasError(formField, errorMsg) {
    const msgEl = getMsgEl(formField);
    if (!msgEl) throw new Error('Field must have a message element with class "field-message"');

    const fieldInput = formField.querySelector('.form-input');
    if (!fieldInput) throw new Error('Field must have a form-input element');
    
    msgEl.innerHTML = errorMsg;

    fieldInput.classList.add('invalid-field');
    fieldInput.addEventListener('input', () => {
        fieldInput.classList.remove('invalid-field');
        msgEl.innerHTML = '';
    });
};


/**
 * Clears the error messages from the form fields
 * @param {HTMLFormElement} form The form to clear the error messages from
 */
function clearFieldErrors(form){
    form.querySelectorAll('.form-input').forEach(input => {
        input.classList.remove('invalid-field');
    });
    form.querySelectorAll('.field-message').forEach(msgEl => {
        msgEl.innerHTML = '';
    });
};


/**
 * Checks if the email is valid 
 * @param {string} email The email to validate
 * @returns {boolean} true if the email is valid, false otherwise
 */
function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9_.]+@[a-zA-Z0-9\._]+\.[a-z]{2,}$/;
    return emailRegex.test(email);
};


/**
 * Checks if the password is valid and sets custom validity message if not
 * @param {Element} passwordInput1 The first password input field
 * @param {Element} passwordInput2 The second password input field
 * @returns {boolean} true if the password is valid, false otherwise
 */
function validatePassword(passwordInput1, passwordInput2) { 
    const specialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?\s]+/;
    if (!specialChars.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password must contain at least 1 special character');
        return false;
    }
    if (!/\d/.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password must contain a number');
        return false;
    }
    if (/^\d$/.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password cannot be all numbers');
        return false;
    }
    if (passwordInput1.value.length < 8) {
        formFieldHasError(passwordInput1.parentElement, 'Password must be at least 8 characters');
        return false;
    }
    if (passwordInput1.value !== passwordInput2.value) {
        formFieldHasError(passwordInput2.parentElement, 'Passwords do not match');
        return false;
    } 
    return true;
};


/**
 * Adds the `onPost` and `onResponse` functions to the form submit button
 * @param {HTMLButtonElement} formCardButton The submit button of the form
 * @param {string} onClickText The text to display on the button when clicked until the response is received(when `onResponse` is called)
 */
function addOnPostAndOnResponseFuncAttr(formCardButton, onClickText){
    let initialText = formCardButton.innerHTML;
    formCardButton.onPost = () => {
        formCardButton.disabled = true;
        formCardButton.innerHTML = onClickText;
    };

    formCardButton.onResponse = () => {
        formCardButton.disabled = false;
        formCardButton.innerHTML = initialText;
    };
};


/**
 * Checks if the unhidden and required form input fields have values
 * @param {HTMLFormElement} form The form card form to check
 * @returns {boolean} true if all required fields have values, false otherwise
 */
function checkInputFields(form){
    let isValid = true;
    form.querySelectorAll('.form-input').forEach(input => {
        if (input.required && !input.value && input.type !== 'hidden') {
            isValid = false;
        }
    });
    return isValid;
};


const formCards = document.querySelectorAll('.form-card');
formCards.forEach(formCard => {
    const formCardForm = formCard.querySelector('form');
    const formCardButton = formCardForm.querySelector('button[type="submit"]');
    const formCardButtonOnClickText = 'Processing...';


    // Define a default onPost and onResponse function for the form submit button
    addOnPostAndOnResponseFuncAttr(formCardButton, formCardButtonOnClickText);
    // form card button is disabled by default
    formCardButton.disabled = true;


    formCardForm.addEventListener("keyup", (e) => {
        if(!checkInputFields(formCardForm)){
            formCardButton.disabled = true;
        }else{
            formCardButton.disabled = false;
        }
    });


    formCardForm.addEventListener("change", (e) => {
        if(!checkInputFields(formCardForm)){
            formCardButton.disabled = true;
        }else{
            formCardButton.disabled = false;
        }
    });
});
