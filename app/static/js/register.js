async function handleRegister(event) {
    event.preventDefault();
    
    // Get Elements
    const fullNameInput = document.getElementById('full_name');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const dobInput = document.getElementById('date_of_birth');
    const genderInput = document.getElementById('gender');
    const passwordInput = document.getElementById('password');
    const registerBtn = document.getElementById('registerBtn');
    
    const originalBtnText = registerBtn.innerHTML;
    
    // Get Values
    const full_name = fullNameInput.value;
    const username = usernameInput.value;
    const email = emailInput.value;
    const date_of_birth = dobInput.value;
    const gender = genderInput.value;
    const password = passwordInput.value;
    
    // Validation
    if(password.length < 6) {
        showToast("Password must be at least 6 characters long.", "warning");
        return;
    }

    // Prepare Payload
    const payload = {
        full_name,
        username,
        email,
        date_of_birth,
        gender,
        password
    };

    // Show loading state
    registerBtn.innerHTML = '<span class="loading loading-spinner"></span> Registering...';
    registerBtn.setAttribute('disabled', 'true');
    
    try {
        const response = await apiCall('/auth/register', 'POST', payload);

        if (response && response.ok) {
            // Success
            await Swal.fire({
                icon: 'success',
                title: 'Registration Successful',
                text: 'Please login to continue.',
                timer: 2000,
                showConfirmButton: false
            });
            window.location.href = '/login';
        } else {
            // Handle specific errors from API if possible
            const errorData = await response.json().catch(() => ({}));
            let errorMsg = "Registration failed.";
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorMsg = errorData.detail.map(e => e.msg).join('\n');
                } else {
                    errorMsg = errorData.detail;
                }
            }
            showToast(errorMsg, "error");
        }
    } catch (error) {
        console.error("Registration error:", error);
        showToast("An error occurred during registration. Please try again.", "error");
    } finally {
        // Reset button
        registerBtn.innerHTML = originalBtnText;
        registerBtn.removeAttribute('disabled');
    }
}
