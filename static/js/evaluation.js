document.addEventListener('DOMContentLoaded', function () {
    const resultContainer = document.getElementById('result-container');
    const eligibilityResult = document.getElementById('eligibility-result');
    const evaluateBtn = document.getElementById('evaluate-btn'); //start the evaluation
    const form = document.getElementById('evaluation-form');
    const creditScoreElement = document.querySelector('.credit-score p'); // The element where the score will be displayed

    // Ensure the elements exist
    if (!resultContainer || !eligibilityResult || !creditScoreElement) {
        console.error("Required elements not found in the DOM.");
        return;
    }

    // Function to compute the credit score
    function calculateCreditScore() {
        let totalScore = 0;

        // Get values from the form fields
        const currentlyEmployed = parseInt(document.querySelector('[name="currently_employed"]').value) || 0;
        const monthlySalary = parseInt(document.querySelector('[name="Monthly_Salary"]').value) || 0;
        const loanTerm = parseInt(document.querySelector('[name="Loan_Term"]').value) || 0;
        const haveCoMaker = parseInt(document.querySelector('[name="Co_Maker"]').value) || 0;
        const savingsAccountStatus = parseInt(document.querySelector('[name="Savings_Account"]').value) || 0;
        const assetOwner = parseInt(document.querySelector('[name="Asset_Owner"]').value) || 0;
        const paymentMethod = parseInt(document.querySelector('[name="Payment_Method"]').value) || 0;
        const repaymentSched = parseInt(document.querySelector('[name="Repayment_Schedule"]').value) || 0;

        // Sum up the selected values to calculate total score
        totalScore = currentlyEmployed + monthlySalary + loanTerm + haveCoMaker + savingsAccountStatus +
                     assetOwner + paymentMethod + repaymentSched;

        return totalScore; // Return the computed credit score
    }

    // Attach event listeners to form elements to trigger score calculation on change
    const formElements = document.querySelectorAll('select');
    formElements.forEach(element => {
        element.addEventListener('change', function() {
            // Recalculate score on form field change, but don’t display yet
            calculateCreditScore();
        });
    });

    // Form submission handling
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Disable button during request
        evaluateBtn.disabled = true;

        // Get the form data
        const formData = new FormData(form);

        // Add the calculated credit score to the form data
        const creditScore = calculateCreditScore(); // Call the function to get the current credit score
        formData.append('Credit_Score', creditScore); // Add credit score to form data

        // Log form data for debugging
        for (const [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }

        // Send form data via Fetch API
        fetch('/evaluation', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.eligibility) {
                eligibilityResult.textContent = data.eligibility;
                resultContainer.style.display = 'block';

                // Show the credit score along with the eligibility result
                creditScoreElement.textContent = creditScore; // Set the calculated credit score
                creditScoreElement.style.display = 'block'; // Ensure the credit score is visible
            } else {
                eligibilityResult.textContent = 'An error occurred. Please try again.';
                resultContainer.style.display = 'block';

                // Hide the credit score if there's an error
                creditScoreElement.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            eligibilityResult.textContent = 'An error occurred. Please try again.';
            resultContainer.style.display = 'block';

            // Hide the credit score if there's an error
            creditScoreElement.style.display = 'none';
        })
        .finally(() => {
            evaluateBtn.disabled = false;
        });
    });

});
