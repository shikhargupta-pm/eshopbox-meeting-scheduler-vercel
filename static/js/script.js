document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('scheduleForm');
    const resultCard = document.getElementById('resultCard');
    const emptyState = document.getElementById('emptyState');
    const submitBtn = document.getElementById('submitBtn');
    const bookMeetingBtn = document.getElementById('aeLink');
    const errorModal = document.getElementById('errorModal');
    const confirmationModal = document.getElementById('confirmationModal');
    const closeBtn = document.querySelector('.close-btn');
    const confirmYesBtn = document.getElementById('confirmYesBtn');
    const confirmNoBtn = document.getElementById('confirmNoBtn');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time_slot');

    let formLocked = false;
    let currentFormData = null;
    let currentAEData = null;
    let excludedAEs = []; // Track AEs already shown

    // Set min date to today
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);

    // Make entire date input clickable (not just the calendar icon)
    dateInput.addEventListener('click', function (e) {
        // Use modern showPicker API if available (Chrome 99+, Edge 99+)
        if (this.showPicker) {
            try {
                this.showPicker();
            } catch (err) {
                // If showPicker fails, focus will still work
                this.focus();
            }
        } else {
            // Fallback for older browsers - focus triggers the calendar
            this.focus();
        }
    });

    // Function to check if a date is a blocked weekend
    function isBlockedWeekend(dateStr) {
        const date = new Date(dateStr + 'T00:00:00');
        const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday

        // Block all Sundays
        if (dayOfWeek === 0) {
            return true;
        }

        // Block 2nd and 4th Saturdays
        if (dayOfWeek === 6) {
            const dayOfMonth = date.getDate();
            const weekOfMonth = Math.ceil(dayOfMonth / 7);
            if (weekOfMonth === 2 || weekOfMonth === 4) {
                return true;
            }
        }

        return false;
    }

    // Validate date on change
    dateInput.addEventListener('change', function () {
        if (this.value && isBlockedWeekend(this.value)) {
            alert('This date falls on a blocked weekend (2nd/4th Saturday or Sunday). Please select another date.');
            this.value = '';
        }
        checkFormCompleteness();
    });

    // Check form completeness and enable/disable submit button
    function checkFormCompleteness() {
        const dateValue = dateInput.value;
        const timeValue = timeSelect.value;
        const volumeChecked = document.querySelector('input[name="volume"]:checked');
        const serviceChecked = document.querySelector('input[name="service"]:checked');

        const allFilled = dateValue && timeValue && volumeChecked && serviceChecked;
        submitBtn.disabled = !allFilled;
        submitBtn.style.opacity = allFilled ? '1' : '0.5';
    }

    // Monitor all form inputs for completeness
    dateInput.addEventListener('change', checkFormCompleteness);
    timeSelect.addEventListener('change', checkFormCompleteness);
    document.querySelectorAll('input[name="volume"]').forEach(input => {
        input.addEventListener('change', checkFormCompleteness);
    });
    document.querySelectorAll('input[name="service"]').forEach(input => {
        input.addEventListener('change', checkFormCompleteness);
    });

    // Initialize button as disabled
    checkFormCompleteness();

    // Lock form inputs
    function lockForm() {
        formLocked = true;
        dateInput.disabled = true;
        timeSelect.disabled = true;
        document.querySelectorAll('input[name="volume"]').forEach(input => {
            input.disabled = true;
            input.parentElement.classList.add('disabled');
        });
        document.querySelectorAll('input[name="service"]').forEach(input => {
            input.disabled = true;
            input.parentElement.classList.add('disabled');
        });
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
    }

    // Submit form
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        if (formLocked) return;

        // Validate all fields are filled
        const volumeChecked = document.querySelector('input[name="volume"]:checked');
        const serviceChecked = document.querySelector('input[name="service"]:checked');

        if (!dateInput.value || !timeSelect.value || !volumeChecked || !serviceChecked) {
            alert('Please fill in all fields before submitting.');
            return;
        }

        // Button Loading State
        const originalBtnText = submitBtn.innerText;
        submitBtn.innerText = 'Finding best match...';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';

        // Prepare Data
        currentFormData = {
            date: dateInput.value,
            time_slot: timeSelect.value,
            volume: volumeChecked.value,
            service: serviceChecked.value,
            exclude: excludedAEs.join(',') // Send list of excluded AEs
        };

        // API Call
        fetchAE(currentFormData, originalBtnText);
    });

    // Book Meeting button click handler
    bookMeetingBtn.addEventListener('click', function (e) {
        // Prevent the default link navigation
        e.preventDefault();
        e.stopPropagation();

        // Get the calendar link URL
        const calendarUrl = this.getAttribute('href');

        // Open the calendar link in a new tab
        window.open(calendarUrl, '_blank', 'noopener,noreferrer');

        // Show confirmation modal after a short delay
        setTimeout(() => {
            confirmationModal.classList.remove('hidden');
        }, 300);
    });

    // Confirmation Modal - Yes button
    confirmYesBtn.addEventListener('click', function () {
        // Close confirmation modal
        confirmationModal.classList.add('hidden');

        // Send booking confirmation to server
        fetch('/confirm_booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAEData),
        })
            .then(response => response.json())
            .then(data => {
                // Show success message
                alert('Booking confirmed! Refreshing to book a new meeting...');

                // Reload the page to reset the form
                window.location.reload();
            })
            .catch((error) => {
                console.error('Error confirming booking:', error);
                alert('Booking recorded. Refreshing page...');
                window.location.reload();
            });
    });

    // Confirmation Modal - No button
    confirmNoBtn.addEventListener('click', function () {
        // Close confirmation modal
        confirmationModal.classList.add('hidden');

        // Add current AE to exclusion list
        const currentAEName = document.getElementById('aeName').innerText;
        if (currentAEName && !excludedAEs.includes(currentAEName)) {
            excludedAEs.push(currentAEName);
        }

        // Show loading state
        resultCard.classList.add('hidden');
        emptyState.classList.remove('hidden');
        submitBtn.innerText = 'Finding another expert...';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';

        // Resend request with updated exclusions
        currentFormData.exclude = excludedAEs.join(',');
        fetchAE(currentFormData, 'Find available expert', true);
    });

    // API fetch function
    function fetchAE(formData, originalBtnText, isFindAnother = false) {
        fetch('/eshopbox_create_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Network error'); });
                }
                return response.json();
            })
            .then(data => {
                // Store current AE data for confirmation
                currentAEData = data;

                // Update Result Card
                document.getElementById('aeName').innerText = data.name;
                document.getElementById('aeEmail').innerText = data.email;
                document.getElementById('aeLink').href = data.calendar_link;

                // Hide empty state, show result
                emptyState.classList.add('hidden');
                resultCard.classList.remove('hidden');

                // Lock form on first submission
                if (!isFindAnother) {
                    lockForm();
                    submitBtn.innerText = 'Match Found!';
                    submitBtn.style.background = 'var(--brand-green)';
                } else {
                    submitBtn.innerText = originalBtnText;
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                errorModal.classList.remove('hidden');

                // Reset Button
                submitBtn.innerText = originalBtnText;
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            });
    }

    // Close Error Modal Logic
    closeBtn.onclick = function () {
        errorModal.classList.add('hidden');
    }

    window.onclick = function (event) {
        if (event.target == errorModal) {
            errorModal.classList.add('hidden');
        }
    }
});
