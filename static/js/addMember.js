var modal = document.getElementById("addMemberModal");
var btn = document.querySelector(".add-member-btn");
var span = document.querySelector(".close-btn");
var membersTableBody = document.querySelector(".members-table tbody");

// Open the "Add New Member" modal
btn.onclick = function() {
    modal.style.display = "block";
}

// Close the modal when the close button is clicked
span.onclick = function() {
    modal.style.display = "none";
}

// Close the modal when clicking outside of it
window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

document.getElementById("addMemberForm").onsubmit = function (e) {
    e.preventDefault(); // Prevent default form submission

    // Validate the form
    if (validateForm(e)) {
        let requiredFields = document.querySelectorAll("#addMemberForm input[required]");
        let allValid = true;

        requiredFields.forEach(function (field) {
            if (!field.value) {
                field.style.borderColor = "red";
                allValid = false;
            } else {
                field.style.borderColor = "";
            }
        });

        if (allValid) {
            const formData = new FormData(document.getElementById("addMemberForm"));

            fetch("/members", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Dynamically create the new row
                    let newRow = document.createElement("tr");
                    let applicantName = document.getElementById("lastname").value + " " + document.getElementById("firstname").value;
                    let status = "Pending";
                    newRow.innerHTML = `
                        <td>${document.getElementById("account-number").value}</td>
                        <td>${document.getElementById("lastname").value}</td>
                        <td>${document.getElementById("firstname").value}</td>
                        <td>${document.getElementById("contact-number").value}</td>
                        <td>${document.getElementById("email-address").value}</td>
                        <td>${document.getElementById("date-applied").value}</td>
                        <td>${status}</td>
                        <td class="actions">
                            <button class="approve" 
                                data-email="${document.getElementById("email-address").value}" 
                                data-name="${applicantName}">Approve</button>
                            <button class="decline" onclick="openDeclineModal(this)">Decline</button>
                            <button class="evaluate">Evaluate</button>
                        </td>
                    `;

                    // Append the new row to the table
                    let tableBody = document.querySelector(".members-table tbody");
                    if (tableBody) {
                        tableBody.appendChild(newRow);
                    } else {
                        console.error("Table body not found!");
                    }

                    // Reset the form and close the modal
                    document.getElementById("addMemberForm").reset();
                    alert("New member added successfully!");
                    document.getElementById("addMemberModal").style.display = "none";

                    // Optional: Reload the table or fetch updated members
                    // location.reload();  // Uncomment if you want to reload
                } else {
                    // Handle error from server response
                    alert("Failed to add member! Error: " + data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("A network error occurred. Please try again later.");
            });
        }
    }
};


// document.getElementById("addMemberForm").onsubmit = function(e) {
//     e.preventDefault();  // Prevent form submission to manually handle the process

//     // Validate the form before proceeding
//     if (validateForm(e)) {
//         // Form is valid, proceed with form submission
//         let requiredFields = document.querySelectorAll("#addMemberForm input[required]");
//         let allValid = true;

//         requiredFields.forEach(function(field) {
//             if (!field.value) {
//                 field.style.borderColor = "red"; 
//                 allValid = false;
//             } else {
//                 field.style.borderColor = ""; 
//             }
//         });

//         if (allValid) {
//             // Gather form data
//             const formData = new FormData(document.getElementById("addMemberForm"));

//             // Use fetch to send the data to the server
//             fetch("/members", {
//                 method: "POST",
//                 body: formData
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.success) {
//                     // Dynamically create the new table row
//                     let newRow = document.createElement("tr");
//                     let applicantName = document.getElementById("name").value;
//                     let status = "Pending"; 
//                     newRow.innerHTML = `
//                         <td>${document.getElementById("account-number").value}</td>
//                         <td>${applicantName}</td>
//                         <td>${document.getElementById("contact-number").value}</td>
//                         <td>${document.getElementById("email-address").value}</td>
//                         <td>${document.getElementById("address").value}</td>
//                         <td>${document.getElementById("date-applied").value}</td>
//                         <td>${status}</td>
//                         <td class="actions">
//                             <button class="approve" 
//                                 data-email="${document.getElementById("email-address").value}" data-name="${applicantName}">Approve</button>
//                             <button class="decline"
//                                 data-email="${document.getElementById("email-address").value}" data-name="${applicantName}" onclick="openDeclineModal(this)">Decline</button>
//                             <button class="evaluate">Evaluate</button>
//                         </td>
//                     `;
//                     // Add the new row to the table in the UI
//                     document.querySelector(".members-table tbody").appendChild(newRow);

//                     // Event listener for "Evaluate" button to redirect to evaluation page
//                     newRow.querySelector(".evaluate").addEventListener("click", function() {
//                         window.location.href = "/evaluation";  
//                     });

//                     // Clear the form and close the modal
//                     document.getElementById("addMemberForm").reset();
//                     alert("New member added!");
//                     document.getElementById("addMemberModal").style.display = "none";
//                     location.reload();
//                 } else {
//                      // Show error message if insertion failed
//                      alert("Failed to add member! Error: " + data.error);
//                 }
//             })
//             .catch(error => {      
//                 console.error("Error adding member:", error);
//                 alert("Successfully added a member!"); 
//                 location.reload(); // This will reload the page after the alert   
//             });
//         }
//     } else {
//         //If the validation failed, prevent form submission
//         // alert("Please correct the errors in the form first.");
//     }
// };


// Open the approval modal
function openApproveModal(button) {
    currentApproveEmail = button.getAttribute("data-email"); // Get the email from the clicked approve button
    document.getElementById("approveMemberModal").style.display = "block";
}

// Close the approval modal
function closeApproveModal() {
    document.getElementById("approveMemberModal").style.display = "none";
}

// Confirm the approval and send the email
function confirmApprove() {
    const approveButton = document.querySelector(`.approve[data-email="${currentApproveEmail}"]`);
    const declineButton = approveButton.nextElementSibling;
    const applicantName = approveButton.getAttribute("data-name"); // Get the name from the button
    const accountNumber = approveButton.closest('tr').cells[0].textContent;

    if (currentApproveEmail) {
        fetch('/send_approval_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                recipient: currentApproveEmail,
                applicantName: applicantName, // Send the applicant's name
                accountNumber: accountNumber
             }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                return fetch('/update_member_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        // account_number: approveButton.closest('tr').cells[0].textContent, // Get account number
                        account_number: accountNumber,
                        status: 'Approved' // Set status to "Approved"
                     }),
                });
            } else {
                alert('Error: ' + data.error);
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`You have approved ${applicantName}. A notification has been sent to: ${currentApproveEmail}`);
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            } 
        })
        .catch(error => {
            console.error('Error sending email:', error);
            alert('Failed to send email.');
        });
    }
    closeApproveModal();
}

// Attach event listener to the members table body
membersTableBody.addEventListener('click', function(e) {
    if (e.target.classList.contains('approve')) {
        openApproveModal(e.target); // Open the approval modal
    } 
});

// decline member javascript logic

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