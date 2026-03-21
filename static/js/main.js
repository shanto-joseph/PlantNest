// Main JavaScript for Plant & Gardening Store

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-toggle="popover"]').popover();
    
    // Smooth scrolling for anchor links
    $('a[href*="#"]').not('[href="#"]').not('[href="#0"]').click(function(event) {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top - 100
                }, 1000);
            }
        }
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Add to cart with AJAX
    $('.add-to-cart-btn').click(function(e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        var button = $(this);
        // No loading or added feedback
        button.prop('disabled', true);
        
        $.ajax({
            url: '/orders/add-to-cart/' + productId + '/',
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    // Update cart count and animate icon
                    updateCartCount(true);
                }
                button.prop('disabled', false);
            },
            error: function() {
                button.prop('disabled', false);
            }
        });
    });
    
    // Update cart count
    function updateCartCount(animate) {
        $.get('/orders/cart-count/', function(data) {
            var cartCountElem = $('.cart-count');
            cartCountElem.text(data.count);
            if (animate) {
                var cartIcon = $('.cart-icon');
                cartIcon.addClass('cart-bounce');
                setTimeout(function() {
                    cartIcon.removeClass('cart-bounce');
                }, 500);
            }
        });
    }
    
    // Add cart bounce animation style
    if (!$('style#cart-bounce-style').length) {
        $('head').append('<style id="cart-bounce-style">.cart-bounce { animation: cart-bounce 0.5s; } @keyframes cart-bounce { 0% { transform: scale(1); } 30% { transform: scale(1.3); } 60% { transform: scale(0.9); } 100% { transform: scale(1); } }</style>');
    }
    
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
    
    // Search functionality
    $('#searchInput').on('input', function() {
        var searchTerm = $(this).val().toLowerCase();
        $('.searchable-item').each(function() {
            var text = $(this).text().toLowerCase();
            if (text.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // Form validation
    $('form').submit(function(e) {
        var isValid = true;
        $(this).find('input[required], textarea[required], select[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            $('html, body').animate({
                scrollTop: $('.is-invalid').first().offset().top - 100
            }, 500);
        }
    });
    
    // Quantity input controls
    $('.quantity-btn').click(function() {
        var input = $(this).siblings('input[type="number"]');
        var currentVal = parseInt(input.val()) || 0;
        var max = parseInt(input.attr('max')) || 999;
        var min = parseInt(input.attr('min')) || 1;
        
        if ($(this).hasClass('quantity-plus')) {
            if (currentVal < max) {
                input.val(currentVal + 1);
            }
        } else {
            if (currentVal > min) {
                input.val(currentVal - 1);
            }
        }
        
        input.trigger('change');
    });
    
    // Price range slider
    if ($('#priceRange').length) {
        $('#priceRange').on('input', function() {
            $('#priceValue').text('$' + $(this).val());
        });
    }
    
    // Back to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#backToTop').fadeIn();
        } else {
            $('#backToTop').fadeOut();
        }
    });
    
    $('#backToTop').click(function() {
        $('html, body').animate({scrollTop: 0}, 800);
        return false;
    });
});

// Utility functions
function showNotification(message, type = 'success') {
    var alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    var notification = `
        <div class="alert ${alertClass} alert-dismissible fade show notification" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
    
    $('body').prepend(notification);
    
    setTimeout(function() {
        $('.notification').fadeOut();
    }, 3000);
}

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