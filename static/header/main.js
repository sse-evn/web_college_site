        // Общие функции для всех версий
        function updateDateTime() {
            const now = new Date();
            const months = ['ЯНВАРЯ', 'ФЕВРАЛЯ', 'МАРТА', 'АПРЕЛЯ', 'МАЯ', 'ИЮНЯ', 'ИЮЛЯ', 'АВГУСТА', 'СЕНТЯБРЯ', 'ОКТЯБРЯ', 'НОЯБРЯ', 'ДЕКАБРЯ'];
            
            document.getElementById('current-date').textContent = 
                `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
            
            document.getElementById('current-time').textContent = 
                `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        }

        function getExternalIP() {
            fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('ip-address').textContent = data.ip;
                })
                .catch(() => {
                    document.getElementById('ip-address').textContent = 'недоступен';
                });
        }

        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', function() {
                const lang = this.dataset.lang;
                document.getElementById('current-language').textContent = lang.toUpperCase();
            });
        });

        // Мобильное меню
        document.addEventListener('DOMContentLoaded', function() {
            const menuToggle = document.querySelector('.mobile-menu-toggle');
            const mobileMenu = document.querySelector('.mobile-menu');
            const overlay = document.querySelector('.overlay');
            const dropdownArrows = document.querySelectorAll('.dropdown-arrow');
            
            if (menuToggle) {
                menuToggle.addEventListener('click', function() {
                    this.classList.toggle('active');
                    mobileMenu.classList.toggle('active');
                    overlay.classList.toggle('active');
                    document.body.style.overflow = this.classList.contains('active') ? 'hidden' : '';
                });
            }
            
            if (overlay) {
                overlay.addEventListener('click', function() {
                    menuToggle.classList.remove('active');
                    mobileMenu.classList.remove('active');
                    this.classList.remove('active');
                    document.body.style.overflow = '';
                });
            }
            
            dropdownArrows.forEach(arrow => {
                arrow.addEventListener('click', function(e) {
                    e.preventDefault();
                    const dropdown = this.closest('.menu-link').nextElementSibling;
                    dropdown.classList.toggle('active');
                    this.classList.toggle('fa-chevron-down');
                    this.classList.toggle('fa-chevron-up');
                });
            });
        });

        // Инициализация
        updateDateTime();
        setInterval(updateDateTime, 1000);
        getExternalIP();
