async function handleRegister(event) {
    event.preventDefault();
    
    // Get Elements
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const emailInput = document.getElementById('email');
    const dobInput = document.getElementById('date_of_birth');
    const genderInput = document.getElementById('gender');
    const passwordInput = document.getElementById('password');
    const registerBtn = document.getElementById('registerBtn');
    
    const originalBtnText = registerBtn.innerHTML;
    
    // Get Values
    const first_name = firstNameInput.value;
    const last_name = lastNameInput.value;
    const email = emailInput.value;
    const date_of_birth = dobInput.value;
    const gender = genderInput.value;
    const password = passwordInput.value;
    
    // Validation
    if (!first_name || !last_name || !email || !date_of_birth || !gender || !password) {
        showToast("Harap isi semua kolom, termasuk Jenis Kelamin.", "warning");
        return;
    }

    if(password.length < 6) {
        showToast("Kata sandi minimal 6 karakter.", "warning");
        return;
    }

    // Prepare Payload
    const payload = {
        full_name: `${first_name} ${last_name}`.trim(),
        username: last_name,
        email,
        date_of_birth,
        gender,
        password
    };

    // Show loading state
    registerBtn.innerHTML = '<span class="loading loading-spinner"></span> Mendaftar...';
    registerBtn.setAttribute('disabled', 'true');
    
    try {
        const response = await apiCall('/auth/register', 'POST', payload);

        if (response && response.ok) {
            // Success
            await Swal.fire({
                icon: 'success',
                title: 'Pendaftaran Berhasil',
                text: 'Silakan masuk untuk melanjutkan.',
                timer: 2000,
                showConfirmButton: false
            });
            window.location.href = '/login';
        } else {
            // Handle specific errors from API if possible
            const errorData = await response.json().catch(() => ({}));
            let errorMsg = "Pendaftaran gagal.";
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
        showToast("Terjadi kesalahan saat pendaftaran. Silakan coba lagi.", "error");
    } finally {
        // Reset button
        registerBtn.innerHTML = originalBtnText;
        registerBtn.removeAttribute('disabled');
    }
}
