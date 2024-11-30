function validateForm() {
    var coopIDPattern = /^[A-Za-z0-9]+$/;
    var cooperativeId = document.getElementById("cooperative_id").value;
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    var errorMessage = document.getElementById("error-message");

    if (!coopIDPattern.test(cooperativeId)) {
        errorMessage.textContent = "Cooperative ID must contain letters and numbers only.";
        errorMessage.style.display = "block";
        return false;
    }

    if (contactNumber.length !== 12) {
        errorMessage.textContent = "Contact number must be exactly 12 digits.";
        errorMessage.style.display = "block";
        return false;
    }

    if (password !== confirmPassword) {
        errorMessage.textContent = "Passwords do not match. Please try again.";
        errorMessage.style.display = "block";
        return false;
    }
    
    if (password.length < 8) {
        errorMessage.textContent = "Password must be at least 8 characters long.";
        errorMessage.style.display = "block";
        return false;
    }

    errorMessage.style.display = "none";
    return true;
}
