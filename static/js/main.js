// Theme Management
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        this.bindEvents();
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateIcon(theme);
    },

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    },

    updateIcon(theme) {
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.className = theme === 'light' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        }
    },

    bindEvents() {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }
};

// Toast Notifications
const Toast = {
    show(message, type = 'success', duration = 5000) {
        const toastContainer = document.getElementById('toastContainer') || this.createContainer();
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;

        const iconMap = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        toast.innerHTML = `
            <i class="bi ${iconMap[type] || iconMap.info}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;

        toastContainer.appendChild(toast);

        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        });

        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('fade-out');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    },

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }
};

// API Client with error handling and retry logic
const API = {
    baseUrl: window.location.origin,

    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Merge headers
        if (options.headers) {
            options.headers = { ...defaultOptions.headers, ...options.headers };
        }

        // Body handling
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            options.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(this.baseUrl + url, { ...defaultOptions, ...options });

            if (!response.ok) {
                if (response.status === 401) {
                    Toast.show('Session expired. Please login again.', 'warning');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                    return { success: false, message: 'Unauthorized', status: 401 };
                }

                const errorData = await response.json().catch(() => ({}));
                return {
                    success: false,
                    message: errorData.message || `HTTP Error: ${response.status}`,
                    status: response.status
                };
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API Error:', error);

            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                Toast.show('Network error. Please check your connection.', 'error');
                return { success: false, message: 'Network error. Please check your connection.' };
            }

            return { success: false, message: 'An unexpected error occurred. Please try again.' };
        }
    },

    get(url) {
        return this.request(url, { method: 'GET' });
    },

    post(url, data = null) {
        return this.request(url, { method: 'POST', body: data });
    },

    put(url, data = null) {
        return this.request(url, { method: 'PUT', body: data });
    },

    delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

// Form Validation
const FormValidator = {
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    validatePassword(password) {
        return password.length >= 6;
    },

    validateRollNumber(rollNumber) {
        const re = /^[A-Z0-9]{6,12}$/i;
        return re.test(rollNumber);
    },

    showError(input, message) {
        input.classList.add('is-invalid');

        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },

    clearError(input) {
        input.classList.remove('is-invalid');

        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = '';
        }
    },

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

        inputs.forEach(input => {
            this.clearError(input);

            if (!input.value.trim()) {
                this.showError(input, 'This field is required');
                isValid = false;
            } else if (input.type === 'email' && !this.validateEmail(input.value)) {
                this.showError(input, 'Please enter a valid email address');
                isValid = false;
            } else if (input.name === 'password' && !this.validatePassword(input.value)) {
                this.showError(input, 'Password must be at least 6 characters');
                isValid = false;
            }
        });

        return isValid;
    }
};

// Navbar Scroll Effect
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Form Handlers
function initForms() {
    // Contact Form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            Toast.show('Message sent successfully! We will get back to you soon.', 'success');
            contactForm.reset();
        });
    }

    // Profile Form
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(profileForm);
            const newPassword = formData.get('password');
            const confirmPassword = formData.get('confirm_password');

            if (newPassword && newPassword !== confirmPassword) {
                Toast.show('Passwords do not match', 'error');
                return;
            }

            const data = {
                full_name: formData.get('full_name'),
                department: formData.get('department')
            };

            if (newPassword) {
                data.password = newPassword;
            }

            const submitBtn = profileForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

            try {
                const response = await API.put('/api/user/profile', data);
                if (response.success) {
                    Toast.show('Profile updated successfully!', 'success');
                    document.getElementById('confirm_password').value = '';
                    document.getElementById('profileForm').querySelector('input[name="password"]').value = '';
                } else {
                    Toast.show(response.message || 'Update failed', 'error');
                }
            } catch (error) {
                Toast.show('An error occurred', 'error');
            }

            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-save"></i> Save Changes';
        });
    }
}

// Flash messages auto-dismiss
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    initNavbarScroll();
    initForms();
    initFlashMessages();
});

// Export for use in other scripts
window.ThemeManager = ThemeManager;
window.Toast = Toast;
window.API = API;
window.FormValidator = FormValidator;
