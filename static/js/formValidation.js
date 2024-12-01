// Handle form validation
function validateForm(event) {
    event.preventDefault(); // Prevent the form from submitting immediately

    const accountNumber = document.getElementById('account-number').value;
    const emailAddress = document.getElementById('email-address').value;
    const errorMessage = document.getElementById('error-message');

    // Clear any previous error messages
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';

    // Submit form data via AJAX
    const formData = new FormData(document.getElementById('addMemberForm'));
    
    fetch('/members', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Success: close the modal or show a success message
            alert('Member added successfully!');
            location.reload();  // Reload the page to see the updated list
        } else {
            // Error: Show validation error message
            errorMessage.style.display = 'block';
            errorMessage.textContent = data.error;  // Display the error message from the backend
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'An error occurred while adding the member. Please try again.';
    });
}
