// Customer JavaScript for Plant & Gardening Store

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-hide alerts after 5 seconds
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
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href*="#"]').forEach(function(link) {
        if (link.getAttribute('href') !== '#' && link.getAttribute('href') !== '#0') {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        }
    });
    
    // Add to cart functionality
    initializeAddToCartButtons();
    
    // Initialize cart count on page load
    updateCartCount();
    
    // Quantity controls
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    quantityButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input[type="number"]');
            const currentVal = parseInt(input.value) || 0;
            const max = parseInt(input.getAttribute('max')) || 999;
            const min = parseInt(input.getAttribute('min')) || 1;
            
            if (this.textContent === '+') {
                if (currentVal < max) {
                    input.value = currentVal + 1;
                }
            } else {
                if (currentVal > min) {
                    input.value = currentVal - 1;
                }
            }
            
            // Trigger change event
            input.dispatchEvent(new Event('change'));
        });
    });
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const searchableItems = document.querySelectorAll('.searchable-item');
            
            searchableItems.forEach(function(item) {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('input[required], textarea[required], select[required]');
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    firstInvalid.focus();
                }
            }
        });
    });
    
    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Back to top button
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 100) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Initialize cart count
    updateCartCount();
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in-up');
    });
});

// Initialize Add to Cart functionality
function initializeAddToCartButtons() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(function(button) {
        // Remove any existing click event to prevent double binding
        button.replaceWith(button.cloneNode(true));
    });
    // Re-select after cloning
    const freshButtons = document.querySelectorAll('.add-to-cart-btn');
    freshButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (this.closest('form')) {
                // If in a form, let the form handle it (for detail page non-AJAX fallback)
                return;
            }
            e.preventDefault();
            const productId = this.dataset.productId;
            console.log('Add to Cart clicked', productId);
            
            // Disable button temporarily
            this.disabled = true;
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            
            // Determine quantity: use input if present (detail page), else default to 1 (list page)
            let quantity = 1;
            const form = this.closest('form');
            if (form) {
                const quantityInput = form.querySelector('input[name="quantity"]');
                if (quantityInput && quantityInput.value) {
                    quantity = parseInt(quantityInput.value) || 1;
                }
            }
            // If not in a form or no quantity input, quantity stays 1
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ||
                               document.querySelector('meta[name="csrf-token"]');
            if (!csrfToken) {
                console.error('CSRF token not found');
                this.disabled = false;
                this.innerHTML = originalText;
                return;
            }
            // Make AJAX call to add to cart
            fetch('/orders/add-to-cart/' + productId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken.value ? csrfToken.value : csrfToken.content,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success) {
                    updateCartCount(true);
                    
                    // Show success feedback
                    this.innerHTML = '<i class="fas fa-check"></i> Added!';
                    this.style.background = '#28a745';
                    
                    // Reset button after 2 seconds
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.style.background = '';
                        this.disabled = false;
                    }, 2000);
                } else {
                    throw new Error('Failed to add to cart');
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                
                // Show error feedback
                this.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
                this.style.background = '#dc3545';
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.background = '';
                    this.disabled = false;
                }, 2000);
            });
        });
    });
}

// Utility functions - removed notification system

function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

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

// Cart functions
function updateCartCount(animate = false) {
    fetch('/orders/cart-count/')
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.getElementById('cartCount');
        if (cartCountElement) {
            if (data.count > 0) {
                cartCountElement.textContent = data.count > 99 ? '99+' : data.count;
                cartCountElement.style.display = 'inline-flex';
            } else {
                cartCountElement.style.display = 'none';
            }
        }
        
        // Animate cart icon if requested
        if (animate) {
            const cartIcon = document.querySelector('.cart-icon');
            if (cartIcon) {
                cartIcon.classList.add('cart-bounce');
                setTimeout(() => {
                    cartIcon.classList.remove('cart-bounce');
                }, 500);
            }
            
            // Show mini cart briefly if it's not open
            const miniCartSidebar = document.getElementById('miniCartSidebar');
            if (miniCartSidebar && !miniCartSidebar.classList.contains('active')) {
                // Flash the cart icon
                const cartToggle = document.querySelector('.cart-toggle');
                if (cartToggle) {
                    cartToggle.style.transform = 'scale(1.2)';
                    cartToggle.style.boxShadow = '0 0 20px rgba(64, 145, 108, 0.6)';
                    setTimeout(() => {
                        cartToggle.style.transform = '';
                        cartToggle.style.boxShadow = '';
                    }, 300);
                }
            }
        }
    })
    .catch(error => {
        console.error('Error fetching cart count:', error);
        const cartCountElement = document.getElementById('cartCount');
        if (cartCountElement) {
            cartCountElement.style.display = 'none';
        }
    });
}

// Add cart bounce animation style
(function() {
    if (document.getElementById('cart-bounce-style')) return;
    const style = document.createElement('style');
    style.id = 'cart-bounce-style';
    style.innerHTML = `
        .cart-bounce { 
            animation: cart-bounce 0.5s; 
        } 
        @keyframes cart-bounce { 
            0% { transform: scale(1); } 
            30% { transform: scale(1.3); } 
            60% { transform: scale(0.9); } 
            100% { transform: scale(1); } 
        }
    `;
    document.head.appendChild(style);
})();

// Auto-refresh customer notification count every 60 seconds
// setInterval(updateCustomerNotificationCount, 60000);

// Product functions
function changeQuantity(change, inputId) {
    console.log('changeQuantity called with:', change, inputId);
    const input = document.getElementById(inputId);
    if (!input) {
        console.error('Input element not found with ID:', inputId);
        return;
    }
    
    const currentValue = parseInt(input.value) || 0;
    const maxValue = parseInt(input.max) || 999;
    const minValue = parseInt(input.min) || 1;
    
    console.log('Current value:', currentValue, 'Max:', maxValue, 'Min:', minValue);
    
    const newValue = currentValue + change;
    console.log('New value would be:', newValue);
    
    if (newValue >= minValue && newValue <= maxValue) {
        input.value = newValue;
        input.dispatchEvent(new Event('change'));
        console.log('Quantity updated to:', newValue);
    } else {
        console.log('Value not updated - outside min/max range');
    }
}

// Initialize add to cart buttons when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAddToCartButtons();
    initializeQuantityButtons();
    updateCartCount(); // Load initial cart count
});

// Initialize quantity buttons
function initializeQuantityButtons() {
    // Remove existing event listeners by cloning buttons
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    quantityButtons.forEach(function(button) {
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
    });
    
    // Add event listeners to fresh buttons
    const freshButtons = document.querySelectorAll('.quantity-btn');
    freshButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const change = this.textContent === '+' ? 1 : -1;
            const input = this.parentNode.querySelector('input[type="number"]');
            if (input) {
                changeQuantity(change, input.id);
            }
        });
    });
}