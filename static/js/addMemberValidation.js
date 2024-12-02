function validateForm(event) {
    var accountNumber = document.getElementById("account-number").value;
    var name = document.getElementById("name").value;
    var contactNumber = document.getElementById("contact-number").value;
    var emailAddress = document.getElementById("email-address").value;
    var address = document.getElementById("address").value;
    var dateApplied = document.getElementById("date-applied").value;

    var isValid = true;

    // Account Number validation
    if (accountNumber.length < 8) {
        document.getElementById("account_number_error").textContent = "Account Number must be at least 8 characters long.";
        document.getElementById("account_number_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("account_number_error").style.display = "none";
    }

    // Name validation
    if (name.length > 15) {
        document.getElementById("name_error").textContent = "Name should not exceed to 15 characters";
        document.getElementById("name_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("name_error").style.display = "none";
    }

    // Contact Number validation (pattern already in HTML)
    if (!contactNumber.match(/^(09|\+639)\d{9}$/)) {
        document.getElementById("contact_number_error").textContent = "Contact Number must be in the format 0917XXXXXXX or +639XXXXXXXXX.";
        document.getElementById("contact_number_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("contact_number_error").style.display = "none";
    }

    // Email Address validation
    if (!emailAddress.includes("@") || !emailAddress.includes(".")) {
        document.getElementById("email_address_error").textContent = "Please enter a valid email address.";
        document.getElementById("email_address_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("email_address_error").style.display = "none";
    }

    // Address validation
    if (address.length < 5) {
        document.getElementById("address_error").textContent = "Address must be at least 5 characters long.";
        document.getElementById("address_error").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("address_error").style.display = "none";
    }

    // Date Applied validation
    if (dateApplied === "") {
        document.getElementById("date_applied_error").textContent = "Date Applied cannot be empty.";
        document.getElementById("date_applied_error").style.display = "block";
        isValid = false;
    } else {
        var today = new Date();
        var selectedDate = new Date(dateApplied);

        // Resetting the time component for both dates
        today.setHours(0, 0, 0, 0);
        selectedDate.setHours(0, 0, 0, 0);

        if (selectedDate > today) {
            document.getElementById("date_applied_error").textContent = "Date Applied cannot be a future date.";
            document.getElementById("date_applied_error").style.display = "block";
            isValid = false;
        } else {
            document.getElementById("date_applied_error").style.display = "none";
        }
    }

return isValid;

}

// Listen for the "Clear" button click event
document.getElementById("clearBtn").addEventListener("click", function() {
    // Reset all error messages and styles
    resetValidationState();
});

function resetValidationState() {
    // Reset error messages and hide them
    document.getElementById("account_number_error").style.display = "none";
    document.getElementById("name_error").style.display = "none";
    document.getElementById("contact_number_error").style.display = "none";
    document.getElementById("email_address_error").style.display = "none";
    document.getElementById("address_error").style.display = "none";
    document.getElementById("date_applied_error").style.display = "none";

    // Reset the borders of the input fields
    document.getElementById("account-number").style.borderColor = "";
    document.getElementById("name").style.borderColor = "";
    document.getElementById("contact-number").style.borderColor = "";
    document.getElementById("email-address").style.borderColor = "";
    document.getElementById("address").style.borderColor = "";
    document.getElementById("date-applied").style.borderColor = "";
    
    // Optionally, reset the form inputs to empty or their default values
    // document.getElementById("addMemberForm").reset(); // This already resets the form inputs, so not necessary here unless you want extra control
}

