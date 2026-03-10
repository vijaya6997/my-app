// Mini Freelance - Main JS

// Auto-dismiss flash alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 4000);
    });

    // Theme Switcher Logic
    const themeBtns = document.querySelectorAll('.theme-btn');
    const body = document.body;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark-theme';
    setTheme(savedTheme);

    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            setTheme(theme);
        });
    });

    function setTheme(theme) {
        // Remove all previous themes
        body.classList.remove('midnight-theme', 'light-theme', 'sunset-theme', 'dark-theme');
        // Add current theme
        body.classList.add(theme);

        // Update active state on buttons
        themeBtns.forEach(btn => {
            if (btn.dataset.theme === theme) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Save preference
        localStorage.setItem('theme', theme);
    }
});
