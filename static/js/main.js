document.addEventListener('DOMContentLoaded', function () {
    const burgerIcon = document.getElementById('burgerIcon');
    const mobileMenu = document.getElementById('mobileMenu');

    if (burgerIcon && mobileMenu) {
        // Тоггл меню по клику на бургер
        burgerIcon.addEventListener('click', function (e) {
            e.stopPropagation(); // Предотвращаем всплытие, чтобы не сработал клик по документу
            mobileMenu.classList.toggle('active');
            burgerIcon.classList.toggle('active'); // для крестика (если нужно)
        });

        // Закрываем меню при клике вне его области
        document.addEventListener('click', function (e) {
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

    // --- Логика поиска ---
    const searchIcon = document.querySelector('.search-icon');
    const searchModal = document.getElementById('searchModal');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchIcon && searchModal) {
        let savedScrollY = 0;

        function closeSearchModal() {
            searchModal.classList.remove('active');
            document.body.classList.remove('search-modal-open');
            document.body.style.top = '';
            window.scrollTo(0, savedScrollY);
            searchInput.value = '';
            searchResults.innerHTML = '';
        }

        // Открытие поиска
        searchIcon.addEventListener('click', () => {
            savedScrollY = window.scrollY;
            document.body.classList.add('search-modal-open');
            document.body.style.top = `-${savedScrollY}px`;
            searchModal.classList.add('active');
            setTimeout(() => searchInput.focus(), 100);
        });
        
        // Закрытие по крестику
        searchClose.addEventListener('click', closeSearchModal);
        
        // Закрытие при клике по фону
        searchModal.addEventListener('click', (e) => {
            if (e.target === searchModal) {
                closeSearchModal();
            }
        });
        
        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                closeSearchModal();
            }
        });

        // Принудительный скролл результатов колёсиком
        searchResults.addEventListener('wheel', (e) => {
            e.preventDefault();
            searchResults.scrollBy({ top: e.deltaY, behavior: 'smooth' });
        }, { passive: false });
        
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = e.target.value.trim();
                
                if (query.length >= 2) {
                    fetch('/api/search?q=' + encodeURIComponent(query))
                        .then(res => res.json())
                        .then(data => {
                            searchResults.innerHTML = '';
                            if (data.length === 0) {
                                searchResults.innerHTML = '<p style="text-align:center; color:#666; font-family:\'Gerbera-Regular\'; margin-top:20px;">Ничего не найдено</p>';
                                return;
                            }
                            data.forEach(item => {
                                const el = document.createElement('a');
                                el.href = item.url;
                                el.className = 'search-result-item';
                                
                                const imgHtml = item.image 
                                    ? `<img src="${item.image}" class="search-result-img" alt="">` 
                                    : '<div class="search-result-img" style="background:#eee"></div>';
                                    
                                el.innerHTML = `
                                    ${imgHtml}
                                    <div class="search-result-info">
                                        <h4>${item.title}</h4>
                                        <p>${item.desc}</p>
                                    </div>
                                `;
                                searchResults.appendChild(el);
                            });
                        })
                        .catch(err => {
                            console.error('Ошибка поиска:', err);
                        });
                } else {
                    searchResults.innerHTML = '';
                }
            }, 300);
        });
    }
});