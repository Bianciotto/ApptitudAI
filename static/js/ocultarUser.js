document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const userMenuWrapper = document.querySelector('.user-menu-wrapper');
    if (menuToggle && userMenuWrapper) {
        menuToggle.addEventListener('change', function() {
            if (menuToggle.checked) {
                userMenuWrapper.style.display = 'none';
            } else {
                userMenuWrapper.style.display = '';
            }
        });
    }
});