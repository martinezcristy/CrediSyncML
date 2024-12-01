document.addEventListener("DOMContentLoaded", function() {
    fetch('/get_user')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('coopName').value = data.coop_name;
            document.getElementById('coopShortName').value = data.coop_shortName;
            document.getElementById('address').value = data.address;
            document.getElementById('contactNumber').value = data.contact_number;
            document.getElementById('email').value = data.email;
        }
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        alert('Failed to fetch data.');
    });
});

function updateUser(event) {
    event.preventDefault();
    const coopName = document.getElementById('coopName').value;
    const coopShortName = document.getElementById('coopShortName').value;
    const address = document.getElementById('address').value;
    const contactNumber = document.getElementById('contactNumber').value;
    const email = document.getElementById('email').value;

    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            coop_name: coopName,
            coop_shortName: coopShortName,
            address: address,
            contact_number: contactNumber,
            email: email
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('success-message').textContent = data.message;
            document.getElementById('success-message').style.display = 'block';
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error updating user:', error);
        alert('Failed to update user.');
    });
}
