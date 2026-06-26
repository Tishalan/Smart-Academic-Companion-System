// Main JavaScript file for Smart Academic System

// Global variables
let charts = {};

// Document ready
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Form validation
    $('form').on('submit', function(e) {
        if (!validateForm(this)) {
            e.preventDefault();
        }
    });
    
    // Initialize any data tables
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            pageLength: 10,
            responsive: true
        });
    }
});

// Form validation function
function validateForm(form) {
    let isValid = true;
    const required = $(form).find('[required]');
    
    required.each(function() {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
            isValid = false;
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    // Email validation
    $(form).find('input[type="email"]').each(function() {
        const email = $(this).val();
        if (email && !isValidEmail(email)) {
            $(this).addClass('is-invalid');
            isValid = false;
        }
    });
    
    // Password match
    const password = $(form).find('#password');
    const confirm = $(form).find('#confirm_password');
    
    if (password.length && confirm.length) {
        if (password.val() !== confirm.val()) {
            confirm.addClass('is-invalid');
            isValid = false;
        }
    }
    
    return isValid;
}

// Email validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// API calls
const API = {
    baseUrl: '/api',
    
    get: function(endpoint, data = {}) {
        return $.ajax({
            url: this.baseUrl + endpoint,
            method: 'GET',
            data: data,
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
    },
    
    post: function(endpoint, data = {}) {
        return $.ajax({
            url: this.baseUrl + endpoint,
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
    }
};

// Get CSRF token
function getCSRFToken() {
    return $('input[name="csrf_token"]').val() || '';
}

// Show loading spinner
function showLoading(selector) {
    $(selector).html('<div class="spinner"></div>');
}

// Hide loading spinner
function hideLoading(selector) {
    $(selector).find('.spinner').remove();
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Risk color mapping
function getRiskColor(score) {
    if (score >= 0.7) return '#dc3545';
    if (score >= 0.4) return '#ffc107';
    return '#28a745';
}

// Risk level text
function getRiskLevel(score) {
    if (score >= 0.7) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
}

// Grade to letter
function getGradeLetter(marks, maxMarks = 100) {
    const percentage = (marks / maxMarks) * 100;
    if (percentage >= 80) return 'A';
    if (percentage >= 65) return 'B';
    if (percentage >= 50) return 'C';
    if (percentage >= 40) return 'D';
    return 'F';
}

// Notification system
const Notification = {
    show: function(message, type = 'info') {
        const alert = $(`
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('.container-fluid').prepend(alert);
        
        setTimeout(function() {
            alert.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    },
    
    success: function(message) {
        this.show(message, 'success');
    },
    
    error: function(message) {
        this.show(message, 'danger');
    },
    
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    info: function(message) {
        this.show(message, 'info');
    }
};

// Export functions for use in other scripts
window.API = API;
window.Notification = Notification;
window.formatDate = formatDate;
window.getRiskColor = getRiskColor;
window.getRiskLevel = getRiskLevel;
window.getGradeLetter = getGradeLetter;