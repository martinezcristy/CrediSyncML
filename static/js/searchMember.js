document.getElementById("searchBar").addEventListener("input", function () {
    const searchTerm = this.value.trim().toLowerCase();
    const rows = document.querySelectorAll(".members-table tbody tr");
    let hasVisibleMembers = false;

    rows.forEach(row => {
        // Collect text content from all relevant columns in the row
        const accountNumber = row.querySelector("td:nth-child(1)").textContent.toLowerCase();
        const lastName = row.querySelector("td:nth-child(2)").textContent.toLowerCase();
        const firstName = row.querySelector("td:nth-child(3)").textContent.toLowerCase();
        const email = row.querySelector("td:nth-child(4)").textContent.toLowerCase();
        const status = row.querySelector("td:nth-child(5)").textContent.toLowerCase();

        // Check if any column includes the search term
        if (
            accountNumber.includes(searchTerm) ||
            lastName.includes(searchTerm) ||
            firstName.includes(searchTerm) ||
            email.includes(searchTerm) ||
            status.includes(searchTerm)
        ) {
            row.style.display = ""; // Show row
            hasVisibleMembers = true;
        } else {
            row.style.display = "none"; // Hide row
        }
    });

    // Show or hide the "No search result" message based on visibility
    if (!hasVisibleMembers) {
        document.getElementById("noMembersFound").style.display = "block";
    } else {
        document.getElementById("noMembersFound").style.display = "none";
    }
});