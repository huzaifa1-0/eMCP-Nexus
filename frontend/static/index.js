
    // Define the base URL for your backend API

    let API_BASE_URL = '/api';

    // Modal functionality
    const modal = document.getElementById('loginModal');
    const signInBtn = document.getElementById('signInBtn');
    const closeModalBtn = document.getElementById('closeModal');

    // Connection status elements
    const connectionStatus = document.getElementById('connectionStatus');
    const statusIcon = connectionStatus.querySelector('.status-icon');
    const statusText = connectionStatus.querySelector('.status-text');


    // Function to update connection status
    function updateConnectionStatus(status, message) {
        connectionStatus.classList.remove('hidden', 'connected', 'disconnected', 'connecting');

        switch (status) {
            case 'connected':
                connectionStatus.classList.add('connected');
                statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
                break;
            case 'disconnected':
                connectionStatus.classList.add('disconnected');
                statusIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                break;
            case 'connecting':
                connectionStatus.classList.add('connecting');
                statusIcon.innerHTML = '<div class="spinner"></div>';
                break;
        }

        statusText.textContent = message;
        connectionStatus.classList.remove('hidden');

    }

    // Function to check backend connection - SIMPLIFIED VERSION
    async function checkBackendConnection() {
        updateConnectionStatus('connecting', 'Checking backend connection...');

        try {
            console.log('Testing connection to:', `${API_BASE_URL}/health`);
            
            // Try multiple endpoints in case one fails
            let response;
            try {
                response = await fetch(`${API_BASE_URL}/health`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            } catch (error) {
                // If /health fails, try the root API endpoint
                console.log('Health endpoint failed, trying root API...');
                response = await fetch(`${API_BASE_URL}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            }

            console.log('Response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Backend response:', data);
                
                updateConnectionStatus('connected', 'Connected to backend');

                // Hide status after 3 seconds if connected
                setTimeout(() => {
                    connectionStatus.classList.add('hidden');
                }, 3000);

                return true;
            } else {
                throw new Error(`Server returned ${response.status}`);
            }
        } catch (error) {
            console.error('Backend connection failed:', error);
            updateConnectionStatus('disconnected', `Connection error: ${error.message}`);
            return false;
        }
    }

    // Enhanced fetch with timeout and better error handling
    async function fetchWithTimeout(url, options = {}, timeout = 8000) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(id);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.message || `Server returned ${response.status}`);
            }

            return response;
        } catch (error) {
            clearTimeout(id);

            if (error.name === 'AbortError') {
                throw new Error('Request timeout: Server is not responding');
            } else if (error.name === 'TypeError') {
                throw new Error('Network error: Cannot connect to the server');
            } else {
                throw error;
            }
        }
    }

    // Open modal when sign in button is clicked
    signInBtn.addEventListener('click', async () => {
        // Check backend connection before showing modal
        const isConnected = await checkBackendConnection();

        if (isConnected) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        } else {
            // Show error message if backend is not connected
            alert('Cannot connect to the server. Please make sure the backend is running on localhost:8000\n\nCheck the debug panel (click the Debug button) for more information.');
        }
    });

    // Close modal when X is clicked
    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    });

    // Close modal when clicking outside the modal content
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Re-enable scrolling
        }
    });

    // Function to show the selected form and hide others
    function showForm(formId) {
        // Hide all forms
        document.querySelectorAll('.auth-form').forEach(form => {
            form.classList.remove('active');
        });

        // Show the selected form
        document.getElementById(formId).classList.add('active');

        // Reset messages
        document.querySelectorAll('.message').forEach(message => {
            message.style.display = 'none';
        });
    }

    // Form validation and submission
    document.addEventListener('DOMContentLoaded', function () {
        // Load saved API URL if exists
        const savedApiUrl = localStorage.getItem('apiBaseUrl');
        if (savedApiUrl) {
            API_BASE_URL = savedApiUrl;
        }

        // Check backend connection on page load
        checkBackendConnection();

        // Login form submission - UPDATED AND CORRECTED
        document.getElementById('loginForm').addEventListener('submit', async function (e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const loginButton = this.querySelector('.auth-btn');
            const errorMessage = document.getElementById('loginErrorMessage');
            const successMessage = document.getElementById('loginSuccessMessage');

            // Basic validation
            if (!email || !password) {
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please fill in all fields';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
                return;
            }

            loginButton.disabled = true;
            loginButton.textContent = 'LOGGING IN...';
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';

            try {
                console.log('Attempting login with:', email);
                
                const response = await fetchWithTimeout(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                console.log('Login successful:', data);
                
                // Store the access token
                localStorage.setItem('accessToken', data.access_token);
                localStorage.setItem('userEmail', email);

                successMessage.style.display = 'block';
                errorMessage.style.display = 'none';

                // Redirect to marketplace after successful login
                setTimeout(() => {
                    window.location.href = '/marketplace';
                }, 1500);

            } catch (error) {
                console.error('Login error:', error);
                
                let errorMsg = error.message;
                if (error.message.includes('401') || error.message.includes('Incorrect email or password')) {
                    errorMsg = 'Invalid email or password';
                } else if (error.message.includes('Failed to fetch') || error.message.includes('Network error')) {
                    errorMsg = 'Cannot connect to authentication server. Please check if the backend is running.';
                } else if (error.message.includes('404')) {
                    errorMsg = 'Authentication endpoint not found. Check backend routes.';
                }
                
                errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${errorMsg}`;
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';

                updateConnectionStatus('disconnected', `Login failed: ${error.message}`);
            } finally {
                loginButton.disabled = false;
                loginButton.textContent = 'Log In';
            }
        });

        // Registration form submission - UPDATED AND CORRECTED
        document.getElementById('registerForm').addEventListener('submit', async function (e) {
            e.preventDefault();

            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            const registerButton = this.querySelector('.auth-btn');
            const errorMessage = document.getElementById('registerErrorMessage');
            const successMessage = document.getElementById('registerSuccessMessage');

            // Client-side validation
            if (password !== confirmPassword) {
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Passwords do not match';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
                return;
            }

            if (password.length < 6) {
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Password must be at least 6 characters';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
                return;
            }

            if (!username || !email || !password) {
                errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please fill in all fields';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
                return;
            }

            registerButton.disabled = true;
            registerButton.textContent = 'CREATING ACCOUNT...';
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';

            try {
                console.log('Attempting registration for:', email);
                
                const response = await fetchWithTimeout(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, password }),
                });

                const data = await response.json();
                console.log('Registration successful:', data);
                
                successMessage.style.display = 'block';
                errorMessage.style.display = 'none';

                // Clear form and switch to login after successful registration
                document.getElementById('regUsername').value = '';
                document.getElementById('regEmail').value = '';
                document.getElementById('regPassword').value = '';
                document.getElementById('regConfirmPassword').value = '';

                setTimeout(() => {
                    showForm('loginForm');
                    // Pre-fill the login email
                    document.getElementById('email').value = email;
                }, 1500);

            } catch (error) {
                console.error('Registration error:', error);
                
                let errorMsg = error.message;
                if (error.message.includes('400') && error.message.includes('already registered')) {
                    errorMsg = 'Email already registered';
                } else if (error.message.includes('Failed to fetch') || error.message.includes('Network error')) {
                    errorMsg = 'Cannot connect to authentication server. Please check if the backend is running.';
                } else if (error.message.includes('404')) {
                    errorMsg = 'Registration endpoint not found. Check backend routes.';
                }
                
                errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${errorMsg}`;
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';

                updateConnectionStatus('disconnected', `Registration failed: ${error.message}`);
            } finally {
                registerButton.disabled = false;
                registerButton.textContent = 'Create Account';
            }
        });

        // Placeholder forms for forgot password and verification
        document.getElementById('forgotPasswordForm').addEventListener('submit', function (e) {
            e.preventDefault();
            document.getElementById('recoveryInfoMessage').style.display = 'block';
            document.getElementById('recoverySuccessMessage').style.display = 'none';
            
            setTimeout(() => {
                document.getElementById('recoveryInfoMessage').style.display = 'none';
                document.getElementById('recoverySuccessMessage').style.display = 'block';
            }, 1000);
        });

        document.getElementById('verificationForm').addEventListener('submit', function (e) {
            e.preventDefault();
            document.getElementById('verificationSuccessMessage').style.display = 'block';

            setTimeout(function () {
                showForm('loginForm');
            }, 1500);
        });

        // Verification code input handling
        const verificationInputs = document.querySelectorAll('.verification-code input');
        verificationInputs.forEach((input, index) => {
            input.addEventListener('input', function () {
                if (this.value.length === 1 && index < verificationInputs.length - 1) {
                    verificationInputs[index + 1].focus();
                }
            });

            input.addEventListener('keydown', function (e) {
                if (e.key === 'Backspace' && this.value === '' && index > 0) {
                    verificationInputs[index - 1].focus();
                }
            });
        });

        // Resend code functionality
        document.querySelector('.resend-code').addEventListener('click', function() {
            alert('Verification code has been resent to your email.');
        });
    });

    document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
});

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const data = await response.json();
        
        // Update the DOM elements
        // We use data.active_users || 0 to handle cases where DB might be empty
        document.getElementById('stat-users').innerText = data.active_users ?? 0;
        document.getElementById('stat-tools').innerText = data.mcp_tools ?? 0;
        
        // Optional: Update uptime if you decided to make it dynamic later
        if(data.uptime) {
             document.getElementById('stat-uptime').innerText = data.uptime;
        }

    } catch (error) {
        console.error('Error loading stats:', error);
        // Fallback to default values if API fails
        document.getElementById('stat-users').innerText = "100+";
        document.getElementById('stat-tools').innerText = "50+";
    }
}
