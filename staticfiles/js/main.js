document.addEventListener('DOMContentLoaded', () => {

    // Navbar burger toggle
    const navbarBurger = document.querySelector('.navbar-burger');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarBurger && navbarMenu) {
        navbarBurger.addEventListener('click', () => {
            navbarBurger.classList.toggle('is-active');
            navbarMenu.classList.toggle('is-active');
        });
    }

    // Message closing
    const closeMessageButtons = document.querySelectorAll('.close-message');
    closeMessageButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const messageDiv = event.target.closest('.message');
            if (messageDiv) {
                messageDiv.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                messageDiv.style.opacity = '0';
                messageDiv.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    messageDiv.remove();
                }, 300); // Remove after transition
            }
        });
    });

});