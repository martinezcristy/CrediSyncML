document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('.evaluation-form');
    var evaluateButton = document.querySelector('.evaluate-btn');
    
    // Function to enable/disable the Evaluate button based on form validation
    form.addEventListener('input', function () {
        var isFormValid = true;
        form.querySelectorAll('input, select').forEach(function (input) {
            if (input.required && !input.value) {
                isFormValid = false;
            }
        });

        // Enable or disable the button based on form validity
        evaluateButton.disabled = !isFormValid;
    });

    // Handle the button click event to redirect with account number
    evaluateButton.addEventListener('click', function () {
        var accountNumber = "123456"; // Placeholder for account number retrieval
        var accountNumberFromTable = document.querySelector('td.account-number'); // Get account number from the table or form
        
        // If account number is available, use it
        if (accountNumberFromTable) {
            accountNumber = accountNumberFromTable.textContent.trim();
        }

        // If account number is found, redirect
        if (accountNumber) {
            window.location.href = "/evaluation?account_number=" + accountNumber;
        } else {
            alert("Account number not provided.");
        }
    });
});
