document.addEventListener("DOMContentLoaded", function() {
    fetch('/get_user')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                document.getElementById('coopID').value = data.cooperative_id;
                document.getElementById('coopName').value = data.cooperative_name;
                document.getElementById('address').value = data.address;
                document.getElementById('contactNumber').value = data.contact_number;
                document.getElementById('email').value = data.email;
            }
        })
        .catch(error => console.error('Error fetching user data:', error));
});

function updateUser(event) {
    event.preventDefault();

    const user = {
        cooperative_id: document.getElementById('coopID').value,
        coop_name: document.getElementById('coopName').value,
        address: document.getElementById('address').value,
        contact_number: document.getElementById('contactNumber').value,
        email: document.getElementById('email').value
    };

    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error updating user:', error));
}