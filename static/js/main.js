
document.addEventListener('DOMContentLoaded', function() {
    const burgerIcon = document.getElementById('burgerIcon');
    const mobileMenu = document.getElementById('mobileMenu');

    if (burgerIcon && mobileMenu) {
        // Тоггл меню по клику на бургер
        burgerIcon.addEventListener('click', function(e) {
            e.stopPropagation(); // Предотвращаем всплытие, чтобы не сработал клик по документу
            mobileMenu.classList.toggle('active');
            burgerIcon.classList.toggle('active'); // для крестика (если нужно)
        });

        // Закрываем меню при клике вне его области
        document.addEventListener('click', function(e) {
            if (mobileMenu.classList.contains('active') && !mobileMenu.contains(e.target) && e.target !== burgerIcon) {
                mobileMenu.classList.remove('active');
                burgerIcon.classList.remove('active');
            }
        });

        // Закрываем меню при клике по ссылке
        const mobileLinks = mobileMenu.querySelectorAll('.mobile-nav-link');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                burgerIcon.classList.remove('active');
            });
        });
    }
});