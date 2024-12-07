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

// function openDeclineModal(button) {
//     // currentDeclineRow = button.closest("tr"); // Get the row of the clicked decline button
//     currentDeclineEmail = button.getAttribute('data-email'); 
//     document.getElementById("declineMemberModal").style.display = "block";
// }

// function closeDeclineModal() {
//     document.getElementById("declineMemberModal").style.display = "none";
// }

// function confirmDecline() {
 
//     const declineButton = document.querySelector(`.approve[data-email="${currentDeclineEmail}"]`);
//     const applicantName = declineButton.getAttribute("data-name"); // Get the name from the button
//     const accountNumber = declineButton.closest('tr').cells[0].textContent;

//     if (currentDeclineEmail) {
//         fetch('/send_declined_email', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ 
//                 recipient: currentDeclineEmail,
//                 applicantName: applicantName, // Send the applicant's name
//                 accountNumber: accountNumber
//              }),
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.message) {
//                 return fetch('/update_member_status', {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                     },
//                     body: JSON.stringify({ 
//                         account_number: accountNumber,
//                         status: 'Declined' // Set status to "Declined"
//                      }),
//                 });
//             } else {
//                 alert('Error: ' + data.error);
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert(`You have declined ${applicantName}. A notification has been sent to: ${currentDeclineEmail}`);
//                 location.reload();
//             } else {
//                 alert('Error: ' + (data.error || 'Unknown error'));
//             } 
//         })
//         .catch(error => {
//             console.error('Error sending email:', error);
//             alert('Failed to send email.');
//         });
//     }
//     closeDeclineModal();

        
// }