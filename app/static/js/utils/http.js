// Generic HTTP Client Wrapper
const API_BASE = '/api/v1';

/**
 * Executes an HTTP request with Auth headers
 * @param {string} endpoint - The API endpoint (e.g., '/auth/me')
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} body - JSON body or FormData
 * @param {object} customHeaders - Additional headers
 * @returns {Promise<Response|null>}
 */
async function apiCall(endpoint, method = 'GET', body = null, customHeaders = {}) {
    const token = localStorage.getItem('token');
    
    // Default headers
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...customHeaders
    };

    // If body is simple object and we haven't set content-type, assume JSON
    if (body && !headers['Content-Type'] && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
        headers['Content-Type'] = 'application/json';
        body = JSON.stringify(body);
    }

    const options = {
        method,
        headers
    };

    if (body) {
        options.body = body;
    }

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);

        if (res.status === 401) {
            console.warn('Unauthorized access. Redirecting to login.');
            localStorage.removeItem('token');
            // If we are not already on login page
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
            return null;
        }

        return res;
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

/**
 * Specialized helper for Form Data interactions (like Login) 
 * where we might need specific encodings
 */
async function postFormData(endpoint, formData) {
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    };
    
    return fetch(`${API_BASE}${endpoint}`, options);
}

function isAuthenticated() {
    return !!localStorage.getItem('token');
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('token_type');
    window.location.href = '/login';
}
