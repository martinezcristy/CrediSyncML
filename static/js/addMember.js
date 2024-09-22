// Get the modal, button, and close elements
var modal = document.getElementById("addMemberModal");
var btn = document.querySelector(".add-member-btn");
var span = document.querySelector(".close-btn");
var membersTableBody = document.querySelector(".members-table tbody"); // Select the table body

// Ensure modal behavior only happens on the members page
if (window.location.pathname === "/members") {
    // When the "Add New Member" button is clicked, display the modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the close button (X) is clicked, close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks outside the modal, close it
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }

    // Handle form submission (required fields)
    document.getElementById("addMemberForm").onsubmit = function(e) {
        e.preventDefault();
        
        // Check if all required fields are filled
        let requiredFields = document.querySelectorAll("#addMemberForm input[required]");
        let allValid = true;

        requiredFields.forEach(function(field) {
            if (!field.value) {
                field.style.borderColor = "red"; // Highlight the field
                allValid = false;
            } else {
                field.style.borderColor = ""; // Reset the border color if filled
            }
        });

        if (allValid) {
            // Create a new table row
            let newRow = document.createElement("tr");
            newRow.innerHTML = `
                <td>${document.getElementById("account-number").value}</td>
                <td>${document.getElementById("name").value}</td>
                <td>${document.getElementById("contact-number").value}</td>
                <td>${document.getElementById("email-address").value}</td>
                <td>${document.getElementById("address").value}</td>
                <td>${document.getElementById("date-applied").value}</td>
                <td class="actions">
                    <button class="approve">Approve</button>
                    <button class="decline">Decline</button>
                    <button class="evaluate">Evaluate</button>
                </td>
            `;
            membersTableBody.appendChild(newRow); // Append the new row to the table body
            
            alert("New member added!");
            modal.style.display = "none"; 
            document.getElementById("addMemberForm").reset(); // Reset the form fields
        }
    };
}
