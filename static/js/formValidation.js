document.addEventListener('DOMContentLoaded', function() {
    const accountNumberInput = document.getElementById('account-number')
    const nameInput = document.getElementById('name');
    const contactNumberInput = document.getElementById('contact-number');
    const emailInput = document.getElementById('email');
    const form = document.getElementById('my-form');

    // accountNumberInput.addEventListener('')

    contactNumberInput.addEventListener('input', function (e) {
        this.value = this.value.replace(/[^0-9]/g, '');

        if (this.value.length === 11 && this.value.startsWith('0')) {
            this.value = this.value.replace(/^(\d{2})(\d{3})(\d{4})$/, '$1-$2-$3');
        } else if (this.value.length === 13 && this.value.startsWith('+639')) {
            this.value = this.value.replace(/^(\+639)(\d{3})(\d{4})$/, '$1-$2-$3');
        }
    });

    // Form submission validation
    form.addEventListener('submit', function(e) {
        let valid = true;

     
        if (nameInput.value.trim() === '') {
            valid = false;
            alert('Name cannot be empty');
        }
       
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailInput.value)) {
            valid = false;
            alert('Please enter a valid email address');
        }

        const contactNumberPattern = /^(09|\+639)\d{9}$/;
        if (!contactNumberPattern.test(contactNumberInput.value.replace(/-/g, ''))) {
            valid = false;
            alert('Please enter a valid contact number in the format 0917XXXXXXX or +639XXXXXXXXX');
        }

        const accountNumberPattern = /^\d{8}$/;
        if (!accountNumberPattern.test(accountNumberInput.value)) {
            valid = false;
            alert('Account number must be exactly 8 digits');
        }

        if (!valid) {
            e.preventDefault();
        }
    });
});