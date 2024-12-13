// Function to validate form on submit
function validateForm(event) {
    event.preventDefault();  // Prevent form from submitting if validation fails

    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    var isValid = true;

    // Clear any previous error messages
    clearErrorMessages();

    // Validate Password Length
    if (password.length < 8) {
        displayError("password_error", "Password must be at least 8 characters long.");
        isValid = false;
    }

    // Confirm Password Validation
    if (password !== confirmPassword) {
        displayError("confirm_password_error", "Passwords do not match. Please try again.");
        isValid = false;
    }

    // If all validations pass, submit the form
    if (isValid) {
        document.getElementById("signup-form").submit();  // Submit the form if no errors
    }
}

// Function to display error message
function displayError(elementId, message) {
    var errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.style.display = "block";
}

// Function to clear all error messages
function clearErrorMessages() {
    var errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(function(error) {
        error.style.display = "none";
        error.textContent = "";
    });
}

// Event listeners for real-time validation
document.getElementById("password").addEventListener("input", function() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    
    // Validate password length on input
    if (password.length < 8) {
        document.getElementById("password_error").style.display = "block";
    } else {
        document.getElementById("password_error").style.display = "none";
    }
    
    // Validate confirm password on input
    if (password !== confirmPassword) {
        document.getElementById("confirm_password_error").style.display = "block";
    } else {
        document.getElementById("confirm_password_error").style.display = "none";
    }
});

document.getElementById("confirm_password").addEventListener("input", function() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;

    // Check if passwords match during input
    if (password !== confirmPassword) {
        document.getElementById("confirm_password_error").style.display = "block";
    } else {
        document.getElementById("confirm_password_error").style.display = "none";
    }
});

// Attach the validation function to form submit event
document.querySelector("form").addEventListener("submit", validateForm);
