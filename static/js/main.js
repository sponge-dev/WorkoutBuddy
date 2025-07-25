// Main JavaScript file for WorkoutBot
// Common utilities and functions

// Global variables
let currentUser = null;

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Load user data if available
    loadCurrentUser();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize common event listeners
    initializeCommonEvents();
}

// Load current user data
function loadCurrentUser() {
    fetch('/api/user')
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                currentUser = data;
                updateUserInterface();
            }
        })
        .catch(error => {
            console.log('No user data loaded:', error);
        });
}

// Update UI based on user data
function updateUserInterface() {
    if (currentUser) {
        // Update navbar or other UI elements with user info
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(element => {
            element.textContent = currentUser.name;
        });
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize common event listeners
function initializeCommonEvents() {
    // Loading state management
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.tagName === 'FORM') {
            addLoadingState(form);
        }
    });
    
    // Auto-save drafts (for forms with class 'auto-save')
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => debounce(autoSaveForm, 1000)(form));
        });
    });
}

// Utility Functions

// Add loading state to button or form
function addLoadingState(element) {
    const submitBtn = element.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        submitBtn.disabled = true;
        
        // Remove loading state after 5 seconds (fallback)
        setTimeout(() => {
            removeLoadingState(submitBtn, originalText);
        }, 5000);
    }
}

// Remove loading state
function removeLoadingState(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-save form data to localStorage
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    const formId = form.id || 'anonymous-form';
    
    try {
        localStorage.setItem(`workoutbot-draft-${formId}`, JSON.stringify(data));
        showToast('Draft saved automatically', 'info');
    } catch (error) {
        console.error('Failed to auto-save form:', error);
    }
}

// Load auto-saved form data
function loadAutoSavedData(formId) {
    try {
        const savedData = localStorage.getItem(`workoutbot-draft-${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            const form = document.getElementById(formId);
            
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
            
            showToast('Draft restored', 'info');
        }
    } catch (error) {
        console.error('Failed to load auto-saved data:', error);
    }
}

// Clear auto-saved data
function clearAutoSavedData(formId) {
    try {
        localStorage.removeItem(`workoutbot-draft-${formId}`);
    } catch (error) {
        console.error('Failed to clear auto-saved data:', error);
    }
}

// Show toast notification
function showToast(message, type = 'success', duration = 3000) {
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Remove from DOM after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Get appropriate icon for toast type
function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle',
        primary: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Format date for display
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
}

// Format time for display
function formatTime(minutes) {
    if (!minutes) return '0 min';
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins} min`;
}

// Calculate BMI (Imperial units)
function calculateBMI(weight, height) {
    if (!weight || !height || weight <= 0 || height <= 0) {
        return null;
    }
    // BMI = (weight in lbs / height in inches²) × 703
    const bmi = (weight / (height * height)) * 703;
    return Math.round(bmi * 10) / 10;
}

// Profile editing functionality
function openEditProfile() {
    // Check if we're on a page that has the modal
    if (!document.getElementById('userSetupModal')) {
        // Redirect to home page where the modal exists
        window.location.href = '/?edit_profile=true';
        return;
    }
    
    // Load current user data and populate form
    fetch('/api/user')
        .then(response => response.json())
        .then(userData => {
            // Populate form fields
            document.getElementById('userName').value = userData.name || '';
            document.getElementById('userAge').value = userData.age || '';
            document.getElementById('userHeight').value = userData.height || '';
            document.getElementById('userGender').value = userData.gender || '';
            document.getElementById('fitnessLevel').value = userData.fitness_level || '';
            
            // Get latest weight from progress
            fetch('/api/progress')
                .then(response => response.json())
                .then(progressData => {
                    if (progressData.length > 0) {
                        const latestWeight = progressData[progressData.length - 1].weight;
                        document.getElementById('userWeight').value = latestWeight || '';
                    }
                })
                .catch(error => console.log('No progress data found'));
            
            // Set form to editing mode
            document.getElementById('userSetupForm').dataset.editing = 'true';
            document.getElementById('userModalTitle').textContent = 'Update Profile';
            document.getElementById('saveUserBtnText').textContent = 'Update Profile';
            
            // Show modal
            bootstrap.Modal.getOrCreateInstance(document.getElementById('userSetupModal')).show();
        })
        .catch(error => {
            console.error('Error loading user data:', error);
            alert('Error loading profile data. Please try again.');
        });
}

// Format number with appropriate decimals
function formatNumber(number, decimals = 1) {
    if (number === null || number === undefined) return '-';
    return Number(number).toFixed(decimals);
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate phone number format
function isValidPhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// Generate random color for charts
function generateRandomColor(alpha = 1) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Local Storage helpers
const LocalStorage = {
    set: (key, value) => {
        try {
            localStorage.setItem(`workoutbot-${key}`, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(`workoutbot-${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(`workoutbot-${key}`);
            return true;
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
            return false;
        }
    },
    
    clear: () => {
        try {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('workoutbot-')) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (error) {
            console.error('Failed to clear localStorage:', error);
            return false;
        }
    }
};

// API helper functions
const API = {
    request: async (url, options = {}) => {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    get: (url) => API.request(url),
    
    post: (url, data) => API.request(url, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    put: (url, data) => API.request(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    delete: (url) => API.request(url, {
        method: 'DELETE'
    })
};

// Make openEditProfile globally available for navigation
window.openEditProfile = openEditProfile;

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 20;
}

// PWA Support (for mobile installation)
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button if you have one
    const installButton = document.getElementById('install-button');
    if (installButton) {
        installButton.style.display = 'block';
        
        installButton.addEventListener('click', () => {
            installButton.style.display = 'none';
            deferredPrompt.prompt();
            
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                } else {
                    console.log('User dismissed the install prompt');
                }
                deferredPrompt = null;
            });
        });
    }
});

// Service Worker registration (for PWA)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export functions for use in other scripts
window.WorkoutBot = {
    showToast,
    formatDate,
    formatTime,
    calculateBMI,
    openEditProfile,
    formatNumber,
    LocalStorage,
    API,
    addLoadingState,
    removeLoadingState,
    debounce
}; 