document.addEventListener('DOMContentLoaded', () => {
    // CoMaker Toggle Logic
    const coMakerToggle = document.getElementById('co_maker_toggle');
    const coMakerForm = document.getElementById('co-maker-form');

    coMakerToggle.addEventListener('change', () => {
        if (coMakerToggle.checked) {
            coMakerForm.style.display = 'block'; // Show co-maker form
        } else {
            coMakerForm.style.display = 'none'; // Hide co-maker form

            // Clear inputs when form is hidden
            const inputs = coMakerForm.querySelectorAll('input');
            inputs.forEach(input => input.value = '');
        }
    });

    // Assets Toggle Logic
    const assetsToggle = document.getElementById('assets_toggle');
    const assetsForm = document.getElementById('assets-form');

    assetsToggle.addEventListener('change', () => {
        if (assetsToggle.checked) {
            assetsForm.style.display = 'block'; // Show assets form
        } else {
            assetsForm.style.display = 'none'; // Hide assets form

            // Clear inputs when form is hidden
            const inputs = assetsForm.querySelectorAll('input');
            inputs.forEach(input => input.value = '');
        }
    });

    // Form Navigation Logic
    const steps = document.querySelectorAll('.form-step');
    const nextBtns = document.querySelectorAll('.next-btn');
    const prevBtns = document.querySelectorAll('.prev-btn');
    const progressBar = document.getElementById('progress-bar');

    let currentStep = 0;

    // Show the current step
    function showStep(step) {
        steps.forEach((s, index) => {
            s.classList.toggle('active', index === step);
        });

        // Update progress bar
        const progress = ((step + 1) / steps.length) * 100; // Calculate percentage
        progressBar.style.width = `${progress}%`;
    }

    // Validate required inputs for mandatory steps (steps 1-3)
    function validateRequiredInputs(form) {
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

    // Next button logic
    nextBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            const currentForm = steps[currentStep];

            // Validate required inputs only for steps 1-3
            if (currentStep < 3) {
                const isValid = validateRequiredInputs(currentForm);
                if (!isValid) return; // Stop if validation fails
            }

            // Move to the next step if applicable
            if (currentStep < steps.length - 1) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    // Previous button logic
    prevBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Initialize first step and progress bar
    showStep(currentStep);

});
