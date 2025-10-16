// JobHunter Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('JobHunter app initialized');
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                showAlert('Please fill in all required fields.', 'error');
            }
        });
    });
    
    // Alert system
    window.showAlert = function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    };
    
    // Auto-dismiss alerts
    const autoAlerts = document.querySelectorAll('.alert');
    autoAlerts.forEach(alert => {
        setTimeout(() => {
            alert.remove();
        }, 5000);
    });
    
    // Job search functionality
    const searchForm = document.getElementById('job-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const searchParams = new URLSearchParams(formData);
            
            // Simulate search - replace with actual API call
            console.log('Searching jobs with:', Object.fromEntries(formData));
            showAlert('Searching for jobs...', 'info');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// API utility functions
const JobHunterAPI = {
    async getJobs(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await fetch(`/api/jobs?${queryString}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching jobs:', error);
            throw error;
        }
    },
    
    async submitApplication(formData) {
        try {
            const response = await fetch('/api/apply', {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Error submitting application:', error);
            throw error;
        }
    }
};
