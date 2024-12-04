var modal = document.getElementById("addMemberModal");
var btn = document.querySelector(".add-member-btn");
var span = document.querySelector(".close-btn");
var membersTableBody = document.querySelector(".members-table tbody");
var currentDeclineRow; // To store the row to be deleted

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

document.getElementById("addMemberForm").onsubmit = function(e) {
    e.preventDefault();  // Prevent form submission to manually handle the process

    // Validate the form before proceeding
    if (validateForm(e)) {
        // Form is valid, proceed with form submission
        let requiredFields = document.querySelectorAll("#addMemberForm input[required]");
        let allValid = true;

        requiredFields.forEach(function(field) {
            if (!field.value) {
                field.style.borderColor = "red"; 
                allValid = false;
            } else {
                field.style.borderColor = ""; 
            }
        });

        if (allValid) {
            // Gather form data
            const formData = new FormData(document.getElementById("addMemberForm"));

            // Use fetch to send the data to the server
            fetch("/members", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Dynamically create the new table row
                    let newRow = document.createElement("tr");
                    let applicantName = document.getElementById("name").value;
                    let status = "Pending"; 
                    newRow.innerHTML = `
                        <td>${document.getElementById("account-number").value}</td>
                        <td>${applicantName}</td>
                        <td>${document.getElementById("contact-number").value}</td>
                        <td>${document.getElementById("email-address").value}</td>
                        <td>${document.getElementById("address").value}</td>
                        <td>${document.getElementById("date-applied").value}</td>
                        <td>${status}</td>
                        <td class="actions">
                            <button class="approve" 
                                data-email="${document.getElementById("email-address").value}" data-name="${applicantName}">Approve</button>
                            <button class="decline" onclick="openDeclineModal(this)">Decline</button>
                            <button class="evaluate">Evaluate</button>
                        </td>
                    `;
                    // Add the new row to the table in the UI
                    document.querySelector(".members-table tbody").appendChild(newRow);

                    // Event listener for "Evaluate" button to redirect to evaluation page
                    newRow.querySelector(".evaluate").addEventListener("click", function() {
                        window.location.href = "/evaluation";  
                    });

                    // Clear the form and close the modal
                    document.getElementById("addMemberForm").reset();
                    alert("New member added!");
                    document.getElementById("addMemberModal").style.display = "none";
                    location.reload();
                } else {
                     // Show error message if insertion failed
                     alert("Failed to add member! Error: " + data.error);
                }
            })
            .catch(error => {      
                console.error("Error adding member:", error);
                alert("Successfully added a member!"); 
                location.reload(); // This will reload the page after the alert   
            });
        }
    } else {
        //If the validation failed, prevent form submission
        // alert("Please correct the errors in the form first.");
    }
};


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
    if (currentApproveEmail) {
        fetch('/send_approval_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                recipient: currentApproveEmail,
                applicantName: applicantName // Send the applicant's name
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
                        account_number: approveButton.closest('tr').cells[0].textContent, // Get account number
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
                approveButton.style.display = "none"; 
                declineButton.style.display = "none"; 
                approveButton.closest('tr').querySelector('.status-cell').textContent = 'Approved';
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

// Open the decline modal and store the row to be deleted
function openDeclineModal(button) {
    currentDeclineRow = button.closest("tr"); // Store the row to be deleted
    document.getElementById("declineMemberModal").style.display = "block";
}

// Close the decline modal
function closeDeclineModal() {
    document.getElementById("declineMemberModal").style.display = "none";
}

// Confirm the decline and remove the row from the table
function confirmDecline() {
    if (currentDeclineRow) {
        currentDeclineRow.remove(); // Remove the row from the table
        alert("Member declined!");
    }
    closeDeclineModal();
}
