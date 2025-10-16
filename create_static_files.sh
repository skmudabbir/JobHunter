#!/bin/bash

# Create frontend/static directory structure
mkdir -p frontend/static/css
mkdir -p frontend/static/js
mkdir -p frontend/static/images

# Create backend/static directory structure (symlink target)
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/static/images

# Create basic CSS file
cat > frontend/static/css/style.css << 'EOF'
/* JobHunter Main Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

.nav-links a:hover {
    opacity: 0.8;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    transition: background 0.3s;
}

.btn:hover {
    background: #0056b3;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.alert {
    padding: 1rem;
    border-radius: 4px;
    margin: 1rem 0;
}

.alert-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.alert-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.job-list {
    display: grid;
    gap: 1rem;
}

.job-item {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1.5rem;
    background: white;
}

.job-item h3 {
    color: #333;
    margin-bottom: 0.5rem;
}

.job-meta {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.footer {
    background: #343a40;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav-links {
        gap: 1rem;
    }
}
EOF

# Create basic JavaScript file
cat > frontend/static/js/app.js << 'EOF'
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
EOF

# Create placeholder image and favicon
cat > frontend/static/images/placeholder.txt << 'EOF'
Placeholder for images
Add your logo.png, favicon.ico, and other images here
EOF

# Create a simple favicon (base64 encoded 1x1 transparent PNG)
echo -n "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" > frontend/static/images/favicon.ico

# Copy files to backend/static (for symlink target)
cp -r frontend/static/css backend/static/
cp -r frontend/static/js backend/static/
cp -r frontend/static/images backend/static/

echo "Static files created successfully!"
echo "Frontend static structure:"
find frontend/static -type f
echo ""
echo "Backend static structure:"
find backend/static -type f