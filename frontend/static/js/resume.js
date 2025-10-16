// Resume management functionality
class ResumeManager {
    constructor() {
        this.initializeEventListeners();
        this.loadResumes();
    }

    initializeEventListeners() {
        // Resume upload form
        const uploadForm = document.getElementById('resume-upload-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }

        // Add resume button
        const addResumeBtn = document.getElementById('add-resume-btn');
        if (addResumeBtn) {
            addResumeBtn.addEventListener('click', () => this.showUploadForm());
        }
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/api/upload-resume', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showAlert('Resume uploaded successfully!', 'success');
                form.reset();
                this.loadResumes();
            } else {
                this.showAlert(result.detail || 'Upload failed', 'error');
            }
        } catch (error) {
            this.showAlert('Upload failed: ' + error.message, 'error');
        }
    }

    async loadResumes() {
        try {
            const response = await fetch('/api/resumes');
            const result = await response.json();
            
            const resumeList = document.getElementById('resume-list');
            if (resumeList) {
                if (result.resumes && result.resumes.length > 0) {
                    resumeList.innerHTML = result.resumes.map(resume => `
                        <div class="resume-item">
                            <h4>${resume.filename}</h4>
                            <small>Uploaded: ${new Date(resume.upload_time * 1000).toLocaleDateString()}</small>
                        </div>
                    `).join('');
                } else {
                    resumeList.innerHTML = '<p>No resumes uploaded yet.</p>';
                }
            }
        } catch (error) {
            console.error('Failed to load resumes:', error);
        }
    }

    showUploadForm() {
        // Simple form show/hide - you might want to use a modal
        const uploadForm = document.getElementById('upload-form-container');
        if (uploadForm) {
            uploadForm.style.display = uploadForm.style.display === 'none' ? 'block' : 'none';
        }
    }

    showAlert(message, type) {
        // Use your existing alert system or create one
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        document.body.prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResumeManager();
});