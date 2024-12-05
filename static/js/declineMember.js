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
        // Get account number, email, and applicant name from the current row
        const accountNumber = currentDeclineRow.cells[0].textContent; // Assuming account number is in the first cell (td)
        const recipientEmail = currentDeclineRow.cells[1].textContent; // Assuming email is in the second cell (td)
        const applicantName = currentDeclineRow.cells[2].textContent; // Assuming applicant name is in the third cell (td)

        // Decline member
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

            // Send declined email
            return fetch('/send_declined_email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipient: recipientEmail,
                    applicantName: applicantName
                }), // Sending email and applicant name to backend
            });
        })
        .then(emailResponse => {
            if (!emailResponse.ok) {
                throw new Error('Network response was not ok ' + emailResponse.statusText);
            }
            return emailResponse.json();
        })
        .then(emailData => {
            alert(emailData.message);
            location.reload();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            alert('Failed to decline the member or send the email. Please try again.');
        });
    }
    closeDeclineModal();
}


// var currentDeclineRow; // To store the row to be deleted

// function openDeclineModal(button) {
//     currentDeclineRow = button.closest("tr"); // Get the row of the clicked decline button
//     document.getElementById("declineMemberModal").style.display = "block";
// }

// function closeDeclineModal() {
//     document.getElementById("declineMemberModal").style.display = "none";
// }

// function confirmDecline() {
//     if (currentDeclineRow) {
//         // Get account number from the current row
//         const accountNumber = currentDeclineRow.cells[0].textContent; // Assuming account number is in the first cell (td)

//         fetch('/decline_member', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ account_number: accountNumber }), // Sending account number to backend
//         })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok ' + response.statusText);
//             }
//             return response.json();
//         })
//         .then(data => {
//             alert(data.message);
//             location.reload();
//         })
//         .catch(error => {
//             console.error('There was a problem with the fetch operation:', error);
//             alert('Failed to decline the member. Please try again.');
//         });
//     }
//     closeDeclineModal();
// }
