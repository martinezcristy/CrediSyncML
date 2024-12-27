document.addEventListener('DOMContentLoaded', () => {
    // Toggle Form Sections
    function setupToggle(toggleId, formId) {
        const toggle = document.getElementById(toggleId);
        const form = document.getElementById(formId);

        toggle.addEventListener('change', () => {
            const inputs = form.querySelectorAll('input, select');
            if (toggle.checked) {
                form.style.display = 'block'; // Show form
                inputs.forEach(input => input.required = true); // Make inputs required
            } else {
                form.style.display = 'none'; // Hide form
                inputs.forEach(input => {
                    input.required = false; // Remove required attribute
                    input.value = ''; // Clear inputs
                });
            }
        });
    }

    // Initialize toggles
    setupToggle('co_maker_toggle', 'co-maker-form');
    setupToggle('assets_toggle', 'assets-form');

    // Multi-Step Form Logic
    const steps = document.querySelectorAll('.form-step');
    const nextBtns = document.querySelectorAll('.next-btn');
    const prevBtns = document.querySelectorAll('.prev-btn');
    const progressBar = document.getElementById('progress-bar');

    let currentStep = 0;

    function showStep(step) {
        steps.forEach((s, index) => s.classList.toggle('active', index === step));
        const progress = ((step + 1) / steps.length) * 100; // Update progress bar
        progressBar.style.width = `${progress}%`;
    }

    function validateInputs(form) {
        const requiredInputs = form.querySelectorAll('input:required, select:required');
        let valid = true;

        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                valid = false;
                input.classList.add('invalid'); // Highlight invalid inputs
            } else {
                input.classList.remove('invalid');
            }
        });

        return valid;
    }

    nextBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            const currentForm = steps[currentStep];
            if (currentStep < steps.length - 1 && validateInputs(currentForm)) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    prevBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    showStep(currentStep); // Initialize first step

    // Handle Form Submission
    const loanForm = document.getElementById('loan-application-form');
    loanForm.addEventListener('submit', (e) => {
        if (!validateInputs(loanForm)) {
            e.preventDefault(); // Prevent submission if validation fails
            alert('Please fill out all required fields.');
        }
    });
});
