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
                        <td>${document.getElementById("email-address").value}</td>
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
                        loan_status: 'Approved' // Set status to "Approved"
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
