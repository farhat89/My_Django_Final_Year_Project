document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    initializeSidebar();
    initializeUpload();
    initializeNotifications();
    updateStorageUsed();
    
    // Sidebar functionality remains the same
    function initializeSidebar() {
        const sidebarToggle = document.querySelector('.navbar-toggler');
        const sidebar = document.querySelector('.sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
                toggleSidebarOverlay();
            });
        }
    }

    // Overlay functionality remains the same
    function toggleSidebarOverlay() {
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
            
            overlay.addEventListener('click', function() {
                document.querySelector('.sidebar').classList.remove('show');
                overlay.classList.remove('show');
            });
        }
        overlay.classList.toggle('show');
    }

    // Improved file upload functionality
    function initializeUpload() {
        const quickUploadBtn = document.querySelector('.btn-primary');
        if (quickUploadBtn) {
            quickUploadBtn.addEventListener('click', function() {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.multiple = true;
                fileInput.accept = '*/*'; // You can restrict file types here
                fileInput.style.display = 'none';
                
                document.body.appendChild(fileInput);
                fileInput.click();
                
                fileInput.addEventListener('change', function(e) {
                    handleFileUpload(e.target.files);
                    document.body.removeChild(fileInput);
                });
            });
        }
    }

    function handleFileUpload(files) {
        if (!files.length) return;
    
        // Create progress indicator
        const progressDiv = document.createElement('div');
        progressDiv.className = 'upload-progress alert alert-info';
        progressDiv.innerHTML = `
            <div class="upload-status">Uploading ${files.length} file(s)...</div>
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
        `;
        document.querySelector('main').insertBefore(progressDiv, document.querySelector('main').firstChild);
    
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file); // Ensure this matches Django's view
        });
    
        // Get CSRF token from cookies
        const csrftoken = getCsrfToken();
    
        fetch('/auth/api/upload/', { // Correct URL to match your Django endpoint
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                progressDiv.className = 'alert alert-success';
                progressDiv.innerHTML = `Successfully uploaded ${files.length} file(s)!`;
    
                // Refresh relevant UI sections
                updateRecentActivity();
                updateRecentFiles();
                updateStorageUsed();
            } else {
                throw new Error(data.message || 'An unknown error occurred.');
            }
        })
        .catch(error => {
            progressDiv.className = 'alert alert-danger';
            progressDiv.innerHTML = `Upload failed: ${error.message}`;
            console.error('Upload error:', error);
        })
        .finally(() => {
            // Remove the progress indicator after 3 seconds
            setTimeout(() => {
                progressDiv.remove();
            }, 3000);
        });
    }
    
    // Helper function to get CSRF token from cookies
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Update recent activity with error handling
    function updateRecentActivity() {
        fetch('/auth/api/recent-activity/')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch recent activity');
            return response.json();
        })
        .then(data => {
            const activityList = document.querySelector('.recent-activities');
            if (activityList && data.activities) {
                activityList.innerHTML = data.activities.map(activity => `
                    <div class="activity-item">
                        <div class="activity-icon">
                            <i class="bi bi-${activity.icon}"></i>
                        </div>
                        <div class="activity-details">
                            <p>${activity.description}</p>
                            <small class="text-muted">${activity.timestamp}</small>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error updating activity:', error));
    }

    // New function to update recent files
    function updateRecentFiles() {
        fetch('/auth/api/recent-files/')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch recent files');
            return response.json();
        })
        .then(data => {
            const filesList = document.querySelector('.recent-files');
            if (filesList && data.files) {
                filesList.innerHTML = data.files.map(file => `
                    <div class="file-item">
                        <div class="file-icon">
                            <i class="bi bi-file-earmark"></i>
                        </div>
                        <div class="file-details">
                            <p>${file.name}</p>
                            <small class="text-muted">${file.size} - ${file.uploaded_at}</small>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error updating recent files:', error));
    }

    // New function to update storage used
    function updateStorageUsed() {
        fetch('/auth/api/storage-usage/')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch storage usage');
            return response.json();
        })
        .then(data => {
            const storageElement = document.querySelector('.storage-used');
            if (storageElement && data.usage) {
                storageElement.textContent = `${data.usage.used} of ${data.usage.total} used`;
            }
        })
        .catch(error => console.error('Error updating storage usage:', error));
    }

    // Notifications functionality remains the same
    function initializeNotifications() {
        const markAllReadBtn = document.querySelector('[data-action="mark-all-read"]');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                markAllNotificationsAsRead();
            });
        }
    }
});


// logout functionality
document.getElementById('logout-form').addEventListener('submit', function(e) {
    e.preventDefault();
    if (confirm('Are you sure you want to logout?')) {
        this.submit();
    }
});

// Add this to your dashboard's JavaScript file
// search functionalities
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    let searchTimeout;

    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        const query = e.target.value;

        // Add loading state
        searchInput.classList.add('loading');

        // Debounce search requests
        searchTimeout = setTimeout(() => {
            if (query.length > 0) {
                fetch(`/auth/search-files/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        displaySearchResults(data.files);
                    })
                    .catch(error => console.error('Error:', error))
                    .finally(() => {
                        searchInput.classList.remove('loading');
                    });
            } else {
                searchResults.innerHTML = '';
                searchInput.classList.remove('loading');
            }
        }, 300);
    });

    function displaySearchResults(files) {
        if (files.length === 0) {
            searchResults.innerHTML = '<div class="p-3 text-center text-muted">No files found</div>';
            return;
        }

        const html = files.map(file => `
            <div class="search-result-item p-2 border-bottom">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <i class="bi bi-file-text me-2"></i>
                        <span>${file.name}</span>
                    </div>
                    <small class="text-muted">${file.size}</small>
                </div>
                <small class="text-muted">${file.created_at}</small>
            </div>
        `).join('');

        searchResults.innerHTML = html;
    }
});