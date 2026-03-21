// Enhanced Cart JavaScript for Plant & Gardening Store

class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.animateCartItems();
        this.updateCartTotals();
    }

    setupEventListeners() {
        // Quantity change listeners
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleQuantityChange(e.target);
            });
        });

        // Remove item listeners
        document.querySelectorAll('.btn-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleRemoveItem(e);
            });
        });

        // Checkout button
        const checkoutBtn = document.querySelector('.btn-checkout');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', (e) => {
                this.handleCheckout(e);
            });
        }
    }

    animateCartItems() {
        const cartItems = document.querySelectorAll('.cart-item');
        cartItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    handleQuantityChange(input) {
        const itemId = this.extractItemId(input);
        const newQuantity = parseInt(input.value);
        const cartItem = input.closest('.cart-item');

        if (newQuantity < 1) {
            input.value = 1;
            return;
        }

        // Add loading state
        cartItem.classList.add('loading');
        input.classList.add('updating');

        // Update quantity via AJAX
        this.updateQuantityAjax(itemId, newQuantity)
            .then(response => {
                if (response.success) {
                    this.updateItemTotal(cartItem, response.itemTotal);
                    this.updateCartTotals();
                    this.showNotification('Cart updated successfully', 'success');
                } else {
                    throw new Error(response.error || 'Failed to update cart');
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
                this.showNotification('Failed to update cart', 'error');
                // Revert to previous value
                input.value = input.dataset.previousValue || 1;
            })
            .finally(() => {
                cartItem.classList.remove('loading');
                input.classList.remove('updating');
            });
    }

    handleRemoveItem(event) {
        event.preventDefault();
        
        const cartItem = event.target.closest('.cart-item');
        const itemName = cartItem.querySelector('.item-name').textContent;
        
        if (!confirm(`Remove "${itemName}" from your cart?`)) {
            return;
        }

        // Add removing animation
        cartItem.classList.add('removing');
        
        setTimeout(() => {
            // Follow the original link after animation
            window.location.href = event.target.href;
        }, 300);
    }

    handleCheckout(event) {
        const cartItems = document.querySelectorAll('.cart-item');
        
        // Check for out of stock items
        const outOfStockItems = Array.from(cartItems).filter(item => {
            const stockStatus = item.querySelector('.stock-status');
            return stockStatus && stockStatus.classList.contains('stock-out');
        });

        if (outOfStockItems.length > 0) {
            event.preventDefault();
            this.showNotification('Please remove out of stock items before checkout', 'error');
            return;
        }

        // Add loading state to checkout button
        event.target.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        event.target.disabled = true;
    }

    updateQuantityAjax(itemId, quantity) {
        return fetch(`/orders/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCsrfToken(),
            },
            body: `quantity=${quantity}`
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            return response.json();
        });
    }

    updateItemTotal(cartItem, newTotal) {
        const totalElement = cartItem.querySelector('.item-total');
        if (totalElement) {
            totalElement.textContent = `Total: ₹${newTotal}`;
            totalElement.style.animation = 'quantityPulse 0.3s ease-in-out';
        }
    }

    updateCartTotals() {
        // This would typically fetch updated totals from server
        // For now, we'll calculate client-side
        let subtotal = 0;
        
        document.querySelectorAll('.cart-item').forEach(item => {
            const priceText = item.querySelector('.item-price').textContent;
            const price = parseFloat(priceText.replace('₹', '').replace(' each', ''));
            const quantity = parseInt(item.querySelector('.quantity-input').value);
            subtotal += price * quantity;
        });

        // Update summary
        const subtotalElement = document.querySelector('.summary-row .summary-value');
        if (subtotalElement) {
            subtotalElement.textContent = `₹${subtotal.toFixed(2)}`;
        }

        const totalElement = document.querySelector('.total-row .summary-value');
        if (totalElement) {
            totalElement.textContent = `₹${subtotal.toFixed(2)}`;
        }
    }

    extractItemId(element) {
        const onchangeAttr = element.getAttribute('onchange');
        const match = onchangeAttr.match(/updateQuantity\((\d+),/);
        return match ? match[1] : null;
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show cart-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 4 seconds
        setTimeout(() => {
            notification.remove();
        }, 4000);
    }
}

// Utility functions for global use
function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) return;
    
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/orders/cart/update/${itemId}/`;
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    
    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity';
    quantityInput.value = newQuantity;
    
    form.appendChild(csrfInput);
    form.appendChild(quantityInput);
    document.body.appendChild(form);
    form.submit();
}

// Initialize cart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new CartManager();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .cart-notification {
        animation: slideInRight 0.3s ease-out;
    }
`;
document.head.appendChild(style);