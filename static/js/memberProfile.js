document.addEventListener("DOMContentLoaded", function () {
    // Fetch member data when the page loads
    fetch('/profile')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                // Populate the form fields with member data
                document.getElementById('accountNumber').value = data.account_number;
                document.getElementById('firstname').value = data.firstname;
                document.getElementById('lastname').value = data.lastname;
                document.getElementById('email').value = data.email;
                document.getElementById('status').value = data.status;
                document.getElementById('cooperativeId').value = data.cooperative_id;
            }
        })
        .catch(error => console.error('Error fetching member data:', error));
});

function updateMember(event) {
    event.preventDefault();

    // Collect member data from the form
    const member = {
        account_number: document.getElementById('accountNumber').value, // Read-only, for reference
        firstname: document.getElementById('firstname').value,
        lastname: document.getElementById('lastname').value,
        email: document.getElementById('email').value,
        status: document.getElementById('status').value
    };

    // Send the updated data to the server
    fetch('/profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(member)
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message); // Success message
            } else if (data.error) {
                alert(data.error); // Error message
            }
        })
        .catch(error => console.error('Error updating member:', error));
}
