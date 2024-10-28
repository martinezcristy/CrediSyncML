var currentDeclineRow;
var memberIdToDecline;  // To store the member ID to be declined

function openDeclineModal(button) {
    currentDeclineRow = button.closest("tr"); // Get the row of the clicked decline button
    memberIdToDecline = currentDeclineRow.querySelector('input[name="member_id"]').value; // Get the hidden member ID from the row
    document.getElementById("declineMemberModal").style.display = "block";
}

function closeDeclineModal() {
    document.getElementById("declineMemberModal").style.display = "none";
}

function confirmDecline() {
    if (memberIdToDecline) {
        // Send a request to the Flask backend to handle the decline action
        fetch('/declineMember', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ member_id: memberIdToDecline })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message); 
                currentDeclineRow.remove(); 
            } else if (data.error) {
                alert("Error: " + data.error); // Show error message if there's an issue
            }
            closeDeclineModal();
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to decline the member.");
            closeDeclineModal();
        });
    }
}
