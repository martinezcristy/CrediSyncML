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
        currentDeclineRow.remove(); // Remove the row from the table
        alert("Member declined!");
    }
    closeDeclineModal();
}
