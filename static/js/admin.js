// Admin JavaScript for PlantNest

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar functionality
    initializeSidebar();
    
    // Initialize admin tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-hide admin alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(() => alert.remove(), 150);
            }
        });
    }, 5000);
    
    // Admin search functionality
    const searchInputs = document.querySelectorAll('[id$="Search"]');
    searchInputs.forEach(function(searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }, 300));
    });
    
    // Admin filter functionality
    const filterSelects = document.querySelectorAll('[id$="Filter"]');
    filterSelects.forEach(function(filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filterValue = this.value;
            const filterType = this.id.replace('Filter', '').toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(function(row) {
                const dataAttribute = row.dataset[filterType];
                if (!filterValue || dataAttribute === filterValue) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
    
    // Image preview functionality
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const previewId = this.id + 'Preview';
            const preview = document.getElementById(previewId) || document.querySelector('.image-preview');
            
            if (file && preview) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            } else if (preview) {
                preview.innerHTML = `
                    <div class="preview-placeholder">
                        <i class="fas fa-image fa-3x text-muted"></i>
                        <p class="text-muted">Image preview will appear here</p>
                    </div>
                `;
            }
        });
    });
    
    // Auto-generate slug from title
    const titleInputs = document.querySelectorAll('input[name="title"]');
    titleInputs.forEach(function(titleInput) {
        const slugInput = document.querySelector('input[name="slug"]');
        if (slugInput) {
            titleInput.addEventListener('input', function() {
                const title = this.value;
                const slug = title.toLowerCase()
                    .replace(/[^a-z0-9 -]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .trim('-');
                slugInput.value = slug;
            });
        }
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[onclick*="confirmDelete"], .btn-danger[onclick]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
    
    // Status update functionality
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const originalStatus = this.dataset.original;
            const newStatus = this.value;
            
            if (originalStatus !== newStatus) {
                if (confirm(`Change status to ${newStatus}?`)) {
                    // Form will submit automatically
                } else {
                    this.value = originalStatus;
                }
            }
        });
    });
    
    // Statistics update
    updateAdminStatistics();
    
    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('.auto-save-form');
    autoSaveForms.forEach(function(form) {
        let autoSaveTimer;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    console.log('Auto-saving draft...');
                    // Implement auto-save logic here
                }, 30000); // Auto-save every 30 seconds
            });
        });
    });
});

// Initialize Sidebar Functionality
function initializeSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    // Sidebar toggle functionality
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 991) {
                sidebar.classList.toggle('show');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.toggle('active');
                }
            } else {
                sidebar.classList.toggle('collapsed');
            }
        });
    }
    
    // Overlay click to close sidebar
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('active');
        });
    }
    
    // Mobile menu toggle from navbar
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            if (window.innerWidth <= 991) {
                sidebar.classList.add('show');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.add('active');
                }
            }
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991) {
            sidebar.classList.remove('show');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('active');
            }
        }
    });
    
    // Initialize Bootstrap collapse for sidebar submenus
    const collapseLinks = document.querySelectorAll('.sidebar-nav [data-toggle="collapse"]');
    collapseLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetSelector = this.getAttribute('data-target');
            const target = document.querySelector(targetSelector);
            const icon = this.querySelector('.collapse-icon');
            
            if (target) {
                // Use jQuery if available, otherwise manual toggle
                if (typeof $ !== 'undefined') {
                    $(target).collapse('toggle');
                } else {
                    // Manual collapse toggle
                    const isOpen = target.classList.contains('show');
                    
                    if (isOpen) {
                        target.classList.remove('show');
                        target.style.height = '0px';
                        this.setAttribute('aria-expanded', 'false');
                        if (icon) {
                            icon.style.transform = 'rotate(0deg)';
                        }
                    } else {
                        // Close other open menus first
                        document.querySelectorAll('.sidebar-submenu.show').forEach(function(menu) {
                            if (menu !== target) {
                                menu.classList.remove('show');
                                menu.style.height = '0px';
                                const otherLink = document.querySelector(`[data-target="#${menu.id}"]`);
                                if (otherLink) {
                                    otherLink.setAttribute('aria-expanded', 'false');
                                    const otherIcon = otherLink.querySelector('.collapse-icon');
                                    if (otherIcon) {
                                        otherIcon.style.transform = 'rotate(0deg)';
                                    }
                                }
                            }
                        });
                        
                        target.classList.add('show');
                        target.style.height = 'auto';
                        this.setAttribute('aria-expanded', 'true');
                        if (icon) {
                            icon.style.transform = 'rotate(180deg)';
                        }
                    }
                }
            }
        });
        
        // Handle Bootstrap collapse events if jQuery is available
        if (typeof $ !== 'undefined') {
            const targetSelector = link.getAttribute('data-target');
            const target = document.querySelector(targetSelector);
            const icon = link.querySelector('.collapse-icon');
            
            if (target && icon) {
                $(target).on('show.bs.collapse', function() {
                    icon.style.transform = 'rotate(180deg)';
                    link.setAttribute('aria-expanded', 'true');
                });
                
                $(target).on('hide.bs.collapse', function() {
                    icon.style.transform = 'rotate(0deg)';
                    link.setAttribute('aria-expanded', 'false');
                });
            }
        }
    });
    
    // Set active menu items based on current URL
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    // Remove JavaScript-based active state setting since it's handled in template
    // The template logic is more reliable for determining active states
    
    // Initialize navbar dropdowns
    initializeNavbarDropdowns();
}

// Admin utility functions
function updateAdminStatistics() {
    // Update various statistics on admin pages
    const statElements = document.querySelectorAll('[id$="Count"]');
    statElements.forEach(function(element) {
        const statType = element.id.replace('Count', '').toLowerCase();
        const rows = document.querySelectorAll(`tbody tr[data-${statType}], tbody tr`);
        
        if (statType === 'total') {
            element.textContent = rows.length;
        } else {
            const filteredRows = Array.from(rows).filter(row => {
                return row.dataset[statType] || row.querySelector(`.badge:contains("${statType}")`);
            });
            element.textContent = filteredRows.length;
        }
    });
}

function confirmDelete(itemName) {
    return confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`);
}

function viewDetails(itemId, itemType) {
    console.log(`View ${itemType} details for ID: ${itemId}`);
    // Implement view details functionality
}

function editItem(itemId, itemType) {
    console.log(`Edit ${itemType} for ID: ${itemId}`);
    // Implement edit functionality
}

function toggleStatus(itemId, newStatus) {
    if (confirm(`Change status to ${newStatus}?`)) {
        console.log(`Toggle status for ID: ${itemId} to ${newStatus}`);
        // Implement status toggle functionality
    }
}

function exportData(dataType) {
    console.log(`Export ${dataType} data`);
    // Implement export functionality
}

function printItem(itemId) {
    console.log(`Print item ID: ${itemId}`);
    // Implement print functionality
}

// Debounce function for admin
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Admin notification function
function showAdminNotification(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show admin-notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.insertBefore(notification, document.body.firstChild);
    
    setTimeout(function() {
        notification.classList.remove('show');
        notification.classList.add('fade');
        setTimeout(() => notification.remove(), 150);
    }, 4000);
}

// Notification System Functions
function handleNotificationClick(notificationId, actionUrl) {
    // Mark notification as read
    markNotificationAsRead(notificationId);
    
    // Navigate to action URL if provided
    if (actionUrl && actionUrl !== '#') {
        window.location.href = actionUrl;
    }
}

function markNotificationAsRead(notificationId) {
    fetch(`/admin-panel/notifications/mark-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove unread styling
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('notification-unread');
                const unreadDot = notificationElement.querySelector('.notification-unread-dot');
                if (unreadDot) {
                    unreadDot.remove();
                }
            }
            
            // Update notification count
            updateNotificationCount();
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

function markAllAsRead() {
    fetch('/admin-panel/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove all unread styling
            document.querySelectorAll('.notification-unread').forEach(element => {
                element.classList.remove('notification-unread');
            });
            
            // Remove all unread dots
            document.querySelectorAll('.notification-unread-dot').forEach(dot => {
                dot.remove();
            });
            
            // Update notification count
            updateNotificationCount();
            
            showAdminNotification(`${data.marked_count} notifications marked as read`, 'success');
        }
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
    });
}

function dismissNotification(event, notificationId) {
    event.stopPropagation(); // Prevent notification click
    
    fetch(`/admin-panel/notifications/dismiss/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove notification from DOM
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.style.opacity = '0';
                setTimeout(() => {
                    notificationElement.remove();
                    
                    // Check if no notifications left
                    const remainingNotifications = document.querySelectorAll('.notification-item').length;
                    if (remainingNotifications === 0) {
                        document.getElementById('notificationsList').innerHTML = `
                            <div class="dropdown-item text-center text-muted" id="noNotificationsMessage">
                                <i class="fas fa-bell-slash"></i>
                                <p class="mb-0">No new notifications</p>
                            </div>
                        `;
                    }
                }, 300);
            }
            
            // Update notification count
            updateNotificationCount();
        }
    })
    .catch(error => {
        console.error('Error dismissing notification:', error);
    });
}

function updateNotificationCount() {
    fetch('/admin-panel/notifications/api/unread-count/')
    .then(response => response.json())
    .then(data => {
        const badge = document.getElementById('notificationBadge');
        if (data.count > 0) {
            if (badge) {
                badge.textContent = data.count;
                badge.style.display = 'inline';
            } else {
                // Create badge if it doesn't exist
                const bellIcon = document.querySelector('#notificationsDropdown');
                const newBadge = document.createElement('span');
                newBadge.className = 'badge badge-danger badge-pill notification-count';
                newBadge.id = 'notificationBadge';
                newBadge.textContent = data.count;
                bellIcon.appendChild(newBadge);
            }
        } else {
            if (badge) {
                badge.style.display = 'none';
            }
        }
    })
    .catch(error => {
        console.error('Error updating notification count:', error);
    });
}

function getCsrfToken() {
    // Try multiple methods to get CSRF token
    let token = '';
    
    // Method 1: From form input
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput && csrfInput.value) {
        token = csrfInput.value;
    }
    
    // Method 2: From meta tag
    if (!token) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.getAttribute('content')) {
            token = metaTag.getAttribute('content');
        }
    }
    
    // Method 3: From cookies
    if (!token) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken' && value) {
                token = value;
                break;
            }
        }
    }
    
    return token;
}

// Auto-refresh notifications every 30 seconds
setInterval(updateNotificationCount, 30000);

// Auto-refresh chat notifications every 10 seconds
setInterval(updateChatNotificationCount, 10000);

function updateChatNotificationCount() {
    fetch('/admin-panel/chat/api/rooms/')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let totalUnread = 0;
            data.rooms.forEach(room => {
                totalUnread += room.unread_count;
            });
            
            const badge = document.getElementById('chatNotificationBadge');
            if (totalUnread > 0) {
                badge.textContent = totalUnread;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    })
    .catch(error => console.error('Error fetching chat notification count:', error));
}

// Initialize chat notification count
document.addEventListener('DOMContentLoaded', function() {
    updateChatNotificationCount();
});

// Chart initialization (if needed)
function initializeAdminCharts() {
    // Initialize charts for admin dashboard
    console.log('Initialize admin charts');
}

// Fix: Define initializeNavbarDropdowns to enable Bootstrap dropdowns in the admin navbar
function initializeNavbarDropdowns() {
    // Use Bootstrap's dropdown jQuery plugin to initialize all dropdowns
    $(function () {
        $('.dropdown-toggle').dropdown();
    });
}