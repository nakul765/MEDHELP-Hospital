document.addEventListener("DOMContentLoaded", () => {

    // 1. Preloader Dismissal Handler
    const preloader = document.getElementById('preloader');
    if (preloader) {
        // Dismiss preloader safely after a brief delay
        setTimeout(() => {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }, 800);
    }

    // 2. Mobile Menu Viewport Toggler Execution (FIXED)
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", function () {
            navLinks.classList.toggle("active");
            
            // Toggle icon representation state matching open action
            const icon = menuToggle.querySelector("i");
            if (icon) {
                if (navLinks.classList.contains("active")) {
                    icon.className = "fas fa-times";
                } else {
                    icon.className = "fas fa-bars";
                }
            }
        });
    }

    // 3. Stateful Persistent Mode Switcher Mechanism (FIXED to align with base.html)
    const themeToggleBtn = document.getElementById("theme-toggle");
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const themeIcon = themeToggleBtn.querySelector('i');
            let newTheme = 'light';

            if (currentTheme === 'light' || !currentTheme) {
                newTheme = 'dark';
                if (themeIcon) themeIcon.className = 'fas fa-sun';
            } else {
                newTheme = 'light';
                if (themeIcon) themeIcon.className = 'fas fa-moon';
            }

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // 4. Back To Top Scroll Control Operations
    const backToTop = document.getElementById("back-to-top");
    if (backToTop) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 300) {
                backToTop.classList.add("show");
            } else {
                backToTop.classList.remove("show");
            }
        });

        backToTop.addEventListener("click", function () {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });
    }

    // 5. Counter Animation On Scroll
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const counterObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = Number(counter.getAttribute('data-target')) || 0;
                    let current = 0;
                    const increment = target / 100;

                    const updateCounter = () => {
                        current += increment;
                        if (current < target) {
                            counter.innerText = Math.floor(current);
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.innerText = target;
                        }
                    };

                    updateCounter();
                    observer.unobserve(counter);
                }
            });
        }, {
            threshold: 0.5
        });

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    // 6. Flash Messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 3000);
    });

    // 7. Password Toggle
    const passToggles = document.querySelectorAll('.toggle-password');
    passToggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const input = document.querySelector(this.getAttribute('toggle'));
            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                this.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                this.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
});