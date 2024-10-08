document.addEventListener("DOMContentLoaded", function () {
    const evaluateButton = document.querySelector(".evaluate-btn");
    const formInputs = document.querySelectorAll(".evaluation-form input, .evaluation-form select");
    const toast = document.getElementById("toast"); // Get the toast element

    // Function to show toast message
    function showToast(message) {
        toast.textContent = message; // Set the message
        toast.style.display = 'block'; // Show the toast
        setTimeout(() => {
            toast.style.display = 'none'; // Hide after 3 seconds
        }, 3000);
    }

    // Function to check if all required fields are filled
    function checkRequiredFields() {
        let allFilled = true;

        formInputs.forEach(input => {
            if (input.required && !input.value) {
                allFilled = false;
            }
        });

        evaluateButton.disabled = !allFilled; // Enable or disable the button based on allFilled
    }

    // Add event listeners to each input and select
    formInputs.forEach(input => {
        input.addEventListener("input", checkRequiredFields);
        input.addEventListener("change", checkRequiredFields); // For select elements
    });

    // Add event listener for the Evaluate button
    evaluateButton.addEventListener("click", function(event) {
        // Prevent form submission if fields are not filled
        if (evaluateButton.disabled) {
            event.preventDefault(); // Prevent the default button action
            showToast("Please fill out all required fields."); // Show toast message if button is disabled
        } else {
            // Form submission can happen here if needed
            document.querySelector(".evaluation-form").submit(); // Uncomment if you want to submit
        }
    });

    // Initial check on page load
    checkRequiredFields();
});

function showToast(message) {
    console.log("Please enter all the required fields."); // Debug log
    toast.textContent = message; // Set the message
    toast.style.display = 'block'; // Show the toast
    setTimeout(() => {
        toast.style.display = 'none'; // Hide after 3 seconds
    }, 3000);
}
