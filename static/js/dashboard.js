document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    initializeSidebar();
    initializeUpload();
    initializeNotifications();
    initializeSearch();
    updateStorageUsed();
    updateRecentActivity();
    updateRecentFiles();
    
    // Sidebar functionality
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

    // File upload functionality
    function initializeUpload() {
        const quickUploadBtn = document.querySelector('.btn-primary');
        if (quickUploadBtn) {
            quickUploadBtn.addEventListener('click', function() {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.multiple = true;
                fileInput.accept = '*/*';
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
            formData.append('files', file);
        });
    
        fetch('/auth/api/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN
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
            setTimeout(() => {
                progressDiv.remove();
            }, 3000);
        });
    }

    // Enhanced search functionality 
    function initializeSearch() {
        const searchInput = document.querySelector('.search-input');
        let searchTimeout;
        
        const searchResultsContainer = document.createElement('div');
        searchResultsContainer.className = 'search-results-container position-absolute w-100 bg-white shadow-sm rounded-bottom border mt-1 d-none';
        searchInput.parentElement.appendChild(searchResultsContainer);

        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length > 0) {
                searchResultsContainer.classList.remove('d-none');
                
                searchResultsContainer.innerHTML = `
                    <div class="p-3 text-center">
                        <i class="fas fa-spinner fa-spin me-2"></i> Searching...
                    </div>
                `;

                searchTimeout = setTimeout(() => {
                    fetch(`/auth/search-files/?query=${encodeURIComponent(query)}`, {
                        headers: {
                            'X-CSRFToken': CSRF_TOKEN,
                            'Accept': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.files && data.files.length > 0) {
                            displaySearchResults(data.files, searchResultsContainer);
                        } else {
                            displayNoResults(searchResultsContainer);
                        }
                    })
                    .catch(error => {
                        console.error('Search error:', error);
                        displaySearchError(searchResultsContainer);
                    });
                }, 300);
            } else {
                searchResultsContainer.classList.add('d-none');
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResultsContainer.contains(e.target)) {
                searchResultsContainer.classList.add('d-none');
            }
        });

        // Handle mobile search display
        const mobileSearchToggle = document.querySelector('.navbar-toggler');
        const searchContainer = document.querySelector('.search-input').parentElement;
        
        if (mobileSearchToggle && searchContainer) {
            mobileSearchToggle.addEventListener('click', function() {
                searchContainer.classList.toggle('d-none');
            });
        }
    }

    const fileIconMap = {
        'pdf': 'file-pdf',
        'doc': 'file-word',
        'docx': 'file-word',
        'xls': 'file-excel',
        'xlsx': 'file-excel',
        'ppt': 'file-powerpoint',
        'pptx': 'file-powerpoint',
        'jpg': 'file-image',
        'jpeg': 'file-image',
        'png': 'file-image',
        'gif': 'file-image',
        'zip': 'file-archive',
        'rar': 'file-archive',
        'txt': 'file-alt',
        'default': 'file'
    };

    function getFileIcon(filename) {
        if (!filename) return 'fa-circle-info'; // Default icon for activities without files
        const extension = filename.split('.').pop().toLowerCase();
        return `fa-${fileIconMap[extension] || fileIconMap.default}`;
    }

    function displaySearchResults(files, container) {
        const resultsHTML = files.map(file => `
            <div class="search-result-item p-3 border-bottom hover-bg-light cursor-pointer">
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="fas ${getFileIcon(file.name)} text-primary fa-lg"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center">
                            <strong class="text-truncate me-2">${file.name}</strong>
                            <small class="text-muted">${file.size}</small>
                        </div>
                        <small class="text-muted d-block">Last modified: ${formatDate(file.created_at)}</small>
                    </div>
                </div>
            </div>
        `).join('');
    
        container.innerHTML = `
            <div class="search-results-scroll" style="max-height: 400px; overflow-y: auto;">
                ${resultsHTML}
            </div>
        `;
    
        // Add click handlers for search results
        container.querySelectorAll('.search-result-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                window.location.href = `/auth/files/${files[index].id}`;
            });
        });
    }

    function displayNoResults(container) {
        container.innerHTML = `
            <div class="p-4 text-center text-muted">
                <i class="fas fa-search fa-lg mb-3"></i>
                <p class="mb-0">No matching files found</p>
            </div>
        `;
    }
    
    function displaySearchError(container) {
        container.innerHTML = `
            <div class="p-3 text-center text-danger">
                <i class="fas fa-exclamation-circle me-2"></i> 
                Error performing search. Please try again.
            </div>
        `;
    }

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

    function updateRecentActivity() {
        fetch('/auth/api/recent-activity/', {
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        })
        .then(response => response.json())
        .then(data => {
            const activityList = document.querySelector('.activities-list');
            if (activityList && data.activities) {
                activityList.innerHTML = data.activities.map(activity => {
                    // Choose icon based on activity type or filename
                    const iconClass = activity.filename ? 
                        getFileIcon(activity.filename) : 
                        `fa-${activity.icon || 'circle-info'}`;
                    
                    return `
                        <div class="activity-item">
                            <div class="activity-icon ${activity.type || 'info'}">
                                <i class="fas ${iconClass} fa-lg"></i>
                            </div>
                            <div class="activity-details">
                                <p class="mb-1">${activity.description}</p>
                                <small class="text-muted">${activity.timestamp}</small>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        })
        .catch(error => console.error('Error updating activity:', error));
    }

    function updateRecentFiles() {
        fetch('/auth/api/recent-files/', {
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        })
        .then(response => response.json())
        .then(data => {
            const recentFilesSection = document.querySelector('.recent-files-section');
            if (recentFilesSection && data.files) {
                const recentFiles = data.files.slice(0, 2);
                recentFilesSection.innerHTML = recentFiles.map(file => `
                    <div class="recent-file-item d-flex align-items-center p-2 border-bottom">
                        <div class="me-3">
                            <i class="fas ${getFileIcon(file.name)} text-primary fa-lg"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-medium">${file.name}</div>
                            <small class="text-muted">${file.modified}</small>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error updating recent files:', error));
    }

    function updateStorageUsed() {
        fetch('/auth/api/storage-usage/', {
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        })
        .then(response => response.json())
        .then(data => {
            const storageElement = document.querySelector('.storage-used');
            if (storageElement && data.usage) {
                storageElement.textContent = `${data.usage.used} of ${data.usage.total} used`;
                
                // Update progress bar if it exists
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar && data.usage.percentage) {
                    progressBar.style.width = `${data.usage.percentage}%`;
                    progressBar.setAttribute('aria-valuenow', data.usage.percentage);
                }
            }
        })
        .catch(error => console.error('Error updating storage usage:', error));
    }

    // Notifications functionality
    function initializeNotifications() {
        const markAllReadBtn = document.querySelector('[data-action="mark-all-read"]');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                markAllNotificationsAsRead();
            });
        }
    }

    function markAllNotificationsAsRead() {
        fetch('/auth/api/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const unreadBadge = document.querySelector('.badge.bg-danger');
                if (unreadBadge) {
                    unreadBadge.remove();
                }
                // Refresh notifications list if needed
                updateNotifications();
            }
        })
        .catch(error => console.error('Error marking notifications as read:', error));
    }

    // Logout functionality
    const logoutForm = document.getElementById('logout-form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                this.submit();
            }
        });
    }
});