// Main JavaScript file for the e-commerce store

document.addEventListener('DOMContentLoaded', function() {
    // Update cart badge
    function updateCartBadge() {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            // TODO: Update with actual cart count from backend
            badge.textContent = '0';
        }
    }

    // Handle product quantity changes
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.productId;
            const quantity = this.value;
            // TODO: Update cart quantity via AJAX
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    });
}); 