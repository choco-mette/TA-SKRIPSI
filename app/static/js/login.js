// Login Page DOM Logic

// Check if already logged in
document.addEventListener('DOMContentLoaded', async () => {
    if (isAuthenticated()) {
         try {
            const userRes = await apiCall('/auth/me');
            if (userRes && userRes.ok) {
                const userData = await userRes.json();
                if (userData.role === 'admin') {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/chat';
                }
            } else {
                // Token invalid?
                localStorage.removeItem('token');
            }
        } catch (e) {
             console.error(e);
        }
    }
});

async function handleLogin(event) {
    event.preventDefault();
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    const originalBtnText = loginBtn.innerHTML;
    
    const email = emailInput.value;
    const password = passwordInput.value;
    
    // Show loading state
    loginBtn.innerHTML = '<span class="loading loading-spinner"></span> Logging in...';
    loginBtn.setAttribute('disabled', 'true');
    
    try {
        // Based on OpenAPI: POST /api/v1/auth/login with JSON body { email, password }
        const response = await apiCall('/auth/login', 'POST', { email, password });

        if (response && response.ok) {
            const data = await response.json();
            
            // Assuming the response contains access_token directly or inside data
            // Adjust based on actual response structure if it differs from standard OAuth2
            const token = data.access_token || data.token; 
            const tokenType = data.token_type || 'bearer';

            if (token) {
                localStorage.setItem('token', token);
                localStorage.setItem('token_type', tokenType);
                
                showToast('Login successful! Redirecting...', 'success');

                // Check user role for redirect
                try {
                    // We need to fetch the user profile to know the role
                    // Can't use apiCall here easily because it reads from localStorage which we just set, 
                    // but apiCall logic is fine.
                   
                    const userRes = await apiCall('/auth/me');
                    if (userRes && userRes.ok) {
                        const userData = await userRes.json();
                        setTimeout(() => {
                            if (userData.role === 'admin') { // Adjust based on your role field name (e.g. is_superuser)
                                window.location.href = '/admin'; // Assuming this route exists
                            } else {
                                window.location.href = '/chat';
                            }
                        }, 1000);
                    } else {
                        // Fallback
                         setTimeout(() => {
                            window.location.href = '/chat';
                        }, 1000);
                    }
                } catch (e) {
                     setTimeout(() => {
                        window.location.href = '/chat';
                    }, 1000);
                }
                
            } else {
                showToast('Token missing in response', 'error');
                loginBtn.innerHTML = originalBtnText;
                loginBtn.removeAttribute('disabled');
            }
        } else {
            // handle errors
            let errorMsg = 'Login failed';
            if (response) {
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || JSON.stringify(errorData);
                } catch(e) {}
            }
            
            showToast(errorMsg, 'error');
            loginBtn.innerHTML = originalBtnText;
            loginBtn.removeAttribute('disabled');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('An error occurred. Check console.', 'error');
        loginBtn.innerHTML = originalBtnText;
        loginBtn.removeAttribute('disabled');
    }
}
