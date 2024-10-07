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

// Handle form submission for adding a new member
document.getElementById("addMemberForm").onsubmit = function(e) {
    e.preventDefault();
    
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
                <button class="decline" onclick="openDeclineModal(this)">Decline</button>
                <button class="evaluate">Evaluate</button>
            </td>
        `;
        membersTableBody.appendChild(newRow); 
        
        // Event listener for "Evaluate" button to redirect to evaluation page
        newRow.querySelector(".evaluate").addEventListener("click", function() {
            window.location.href = "/evaluation";  
        });

        alert("New member added!");
        modal.style.display = "none"; 
        document.getElementById("addMemberForm").reset(); 
    }
};

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
