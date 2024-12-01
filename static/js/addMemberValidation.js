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
        document.getElementById("date_applied_error").style.display = "none";
    }

    return isValid;
}

// // Handle form validation
// function validateForm(event) {
//     event.preventDefault(); // Prevent the form from submitting immediately

//     const accountNumber = document.getElementById('account-number').value;
//     const emailAddress = document.getElementById('email-address').value;
//     const errorMessage = document.getElementById('error-message');

//     // Clear any previous error messages
//     errorMessage.style.display = 'none';
//     errorMessage.textContent = '';

//     // Submit form data via AJAX
//     const formData = new FormData(document.getElementById('addMemberForm'));
    
//     fetch('/members', {
//         method: 'POST',
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             // Success: close the modal or show a success message
//             alert('Member added successfully!');
//             location.reload();  // Reload the page to see the updated list
//         } else {
//             // Error: Show validation error message
//             errorMessage.style.display = 'block';
//             errorMessage.textContent = data.error;  // Display the error message from the backend
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         errorMessage.style.display = 'block';
//         errorMessage.textContent = 'An error occurred while adding the member. Please try again.';
//     });
// }
