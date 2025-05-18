document.addEventListener('DOMContentLoaded', function() {
    // Initialize all collapse elements
    const collapseButtons = document.querySelectorAll('[data-toggle="collapse"]');
    
    collapseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const target = document.querySelector(targetId);
            
            if (target) {
                // Toggle the collapse state
                target.classList.toggle('show');
                
                // Update button text and icon
                const icon = this.querySelector('i');
                if (target.classList.contains('show')) {
                    icon.classList.remove('fa-info-circle');
                    icon.classList.add('fa-chevron-up');
                    this.setAttribute('aria-expanded', 'true');
                } else {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-info-circle');
                    this.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });
}); 