var currentDeclineRow; // To store the row to be deleted

function openDeclineModal(button) {
    currentDeclineRow = button.closest("tr"); // Get the row of the clicked decline button
    document.getElementById("declineMemberModal").style.display = "block";
}

function closeDeclineModal() {
    document.getElementById("declineMemberModal").style.display = "none";
}

function confirmDecline() {
    if (currentDeclineRow) {
        // Get account number from the current row
        const accountNumber = currentDeclineRow.cells[0].textContent; // Assuming account number is in the first cell (td)

        fetch('/decline_member', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ account_number: accountNumber }), // Sending account number to backend
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            alert('Failed to decline the member. Please try again.');
        });
    }
    closeDeclineModal();
}
