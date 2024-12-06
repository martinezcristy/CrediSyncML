function validateForm() {
    var coopIDPattern = /^[A-Za-z0-9]+$/;
    var contactNumberPattern = /^(09|\+639)\d{9}$/;
    var cooperativeId = document.getElementById("cooperative_id").value;
    var contactNumber = document.getElementById("contact_number").value;
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirm_password").value;
    var address = document.getElementById("address").value

    var isValid = true;

    // cooperative id
    if (!coopIDPattern.test(cooperativeId)) {
        document.getElementById("cooperative_id_error").textContent = "Cooperative ID must contain letters and numbers only.";
        document.getElementById("cooperative_id_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("cooperative_id_error").style.display = "none";
    }

    //address
    if (address.length < 5) { 
        document.getElementById("address_error").textContent = "Address must be at least 5 characters long."; 
        document.getElementById("address_error").style.display = "block"; 
        isValid = false; 
    } else { 
        document.getElementById("address_error").style.display = "none"; 
    }

    //contact number
    if (contactNumber.length !== 11) {
        document.getElementById("contact_number_error").textContent = "Contact number must be exactly 11 digits.";
        document.getElementById("contact_number_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("contact_number_error").style.display = "none";
    }

    // contact number pattern
    if (!contactNumber.match(contactNumberPattern)) {
        document.getElementById("contact_number_error").textContent = "format e.g. 0917XXXXXXX";
        document.getElementById("contact_number_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("contact_number_error").style.display = "none";
    }

    //password
    if (password.length < 8) {
        document.getElementById("password_error").textContent = "Password must be at least 8 characters long.";
        document.getElementById("password_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("password_error").style.display = "none";
    }

    //confirm password
    if (password !== confirmPassword) {
        document.getElementById("confirm_password_error").textContent = "Passwords do not match. Please try again.";
        document.getElementById("confirm_password_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("confirm_password_error").style.display = "none";
    }

    return isValid;
}
