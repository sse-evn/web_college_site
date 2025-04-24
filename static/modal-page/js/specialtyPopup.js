
// // Дублируем карточки для бесконечного цикла
// const majorsList = document.querySelector('.majors-list');
// const majorCards = document.querySelectorAll('.major-card');
// majorCards.forEach(card => {
//     const clone = card.cloneNode(true);
//     majorsList.appendChild(clone);
// });

// Данные о специальностях
const specialties = {
    cybersecurity: {
        title: "АҚПАРАТТЫҚ ҚАУІПСІЗДІК ЖҮЙЕЛЕРІ",
        subtitle: "АҚПАРАТТЫҚ ҚАУІПСІЗДІК ТЕХНИГІ",
        description: `
            <p>Ақпараттық қауіпсіздік жүйелері мамандығы бойынша білім алушыларға ақпараттық жүйелерді қорғау, киберқауіптерді анықтау және олардың алдын алу сияқты кәсіби дағдыларды үйретуге бағытталған. Олар желілерді қорғау, шифрлау технологияларын қолдану және қауіпсіздік аудитін жүргізу сияқты тапсырмаларды орындай алады.</p>
            <p>Оқу барысында студенттер заманауи қауіпсіздік құралдарымен жұмыс істеуді үйренеді. Бұл мамандық ақпараттық технологиялар саласындағы сұранысқа ие мамандықтардың бірі болып табылады.</p>
        `,
        details: `
            <div class="detail-item">
                <i class="fas fa-book"></i>
                <p><strong>Мамандық:</strong> 06120200 «АҚПАРАТТЫҚ ҚАУІПСІЗДІК ЖҮЙЕЛЕРІ»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-certificate"></i>
                <p><strong>Квалификация:</strong> 4506120103 «Ақпараттық қауіпсіздік технигі»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-clock"></i>
                <p><strong>Оқу мерзімі:</strong> 9 сынып негізінде – 3 жыл 10 ай</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-users"></i>
                <p><strong>Оқу формасы:</strong> Күндізгі</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-globe"></i>
                <p><strong>Оқыту тілі:</strong> Қазақ тілі, орыс тілі</p>
            </div>
        `
    },
    computing: {
        title: "ЕСЕПТЕУ ТЕХНИКАСЫ ЖӘНЕ АҚПАРАТТЫҚ ЖЕЛІЛЕР",
        subtitle: "КОМПЬЮТЕР АППАРАТТЫҚ, ҚАМТАМАСЫЗ ЕТУ ОПЕРАТОРЫ",
        description: `
            <p>Компьютер аппараттық, қамтамасыз ету операторы мамандығы бойынша білім алушыларға компьютерлік желілерді басқару, компьютерлерді жөндеу және техникалық қызмет көрсету, ақпараттық жүйелерді орнату және басқару сияқты кәсіби дағдыларды үйретуге бағытталған. Олар маршрутизаторлар мен коммутаторларды басқару, желілерді жобалау және қауіпсіздікті қамтамасыз ету сияқты кең ауқымды тапсырмаларды орындай алады.</p>
            <p>Оқу барысында студенттер теориялық білімді практикамен ұштастырады, сонымен қатар заманауи IT-жабдықтарымен және бағдарламалық қамтамасыз етумен жұмыс істеуді үйренеді. Оқуды аяқтағаннан кейін түлектердің жұмысқа орналасу мүмкіндігі жоғары, себебі бұл салада мамандарға сұраныс үнемі өсіп келеді.</p>
        `,
        details: `
            <div class="detail-item">
                <i class="fas fa-book"></i>
                <p><strong>Мамандық:</strong> 06120100 «ЕСЕПТЕУ ТЕХНИКАСЫ ЖӘНЕ АҚПАРАТТЫҚ ЖЕЛІЛЕР»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-certificate"></i>
                <p><strong>Квалификация:</strong> 4506120102 «Компьютер желілерін басқару операторы»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-clock"></i>
                <p><strong>Оқу мерзімі:</strong> 9 сынып негізінде – 3 жыл 10 ай</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-users"></i>
                <p><strong>Оқу формасы:</strong> Күндізгі</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-globe"></i>
                <p><strong>Оқыту тілі:</strong> Қазақ тілі, орыс тілі</p>
            </div>
        `
    },
    software: {
        title: "БАҒДАРЛАМАЛЫҚ ҚАМТАМАСЫЗ ЕТУ",
        subtitle: "БАҒДАРЛАМАШЫ",
        description: `
            <p>Бағдарламалық қамтамасыз ету мамандығы бойынша білім алушыларға бағдарламалау тілдерін үйрену, қосымшаларды әзірлеу және бағдарламалық жүйелерді тестілеу сияқты дағдыларды үйретуге бағытталған. Олар веб-қосымшаларды, мобильді қосымшаларды және басқа да бағдарламалық өнімдерді жасай алады.</p>
            <p>Оқу барысында студенттер Python, Java, C++ сияқты танымал бағдарламалау тілдерін меңгереді. Бұл мамандық IT саласындағы ең сұранысқа ие мамандықтардың бірі болып табылады.</p>
        `,
        details: `
            <div class="detail-item">
                <i class="fas fa-book"></i>
                <p><strong>Мамандық:</strong> 06130100 «БАҒДАРЛАМАЛЫҚ ҚАМТАМАСЫЗ ЕТУ»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-certificate"></i>
                <p><strong>Квалификация:</strong> 4506130101 «Бағдарламашы»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-clock"></i>
                <p><strong>Оқу мерзімі:</strong> 9 сынып негізінде – 3 жыл 10 ай</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-users"></i>
                <p><strong>Оқу формасы:</strong> Күндізгі</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-globe"></i>
                <p><strong>Оқыту тілі:</strong> Қазақ тілі, орыс тілі</p>
            </div>
        `
    },
    radio: {
        title: "РАДИОТЕХНИКА, ЭЛЕКТРОНИКА ЖӘНЕ ТЕЛЕКОММУНИКАЦИЯЛАР",
        subtitle: "ТЕЛЕКОММУНИКАЦИЯ ЖЕЛІЛЕРІНІҢ ТЕХНИГІ",
        description: `
            <p>Радиотехника, электроника және телекоммуникациялар мамандығы бойынша білім алушыларға телекоммуникациялық жүйелерді орнату, жөндеу және қызмет көрсету сияқты дағдыларды үйретуге бағытталған. Олар радиожиіліктерді басқару, телекоммуникациялық жабдықтарды орнату және желілерді қызмет көрсету сияқты тапсырмаларды орындай алады.</p>
            <p>Оқу барысында студенттер заманауи телекоммуникациялық технологиялармен жұмыс істеуді үйренеді. Бұл мамандық телекоммуникация саласында сұранысқа ие.</p>
        `,
        details: `
            <div class="detail-item">
                <i class="fas fa-book"></i>
                <p><strong>Мамандық:</strong> 07140900 «РАДИОТЕХНИКА, ЭЛЕКТРОНИКА ЖӘНЕ ТЕЛЕКОММУНИКАЦИЯЛАР»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-certificate"></i>
                <p><strong>Квалификация:</strong> 4507140901 «Телекоммуникация желілерінің технигі»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-clock"></i>
                <p><strong>Оқу мерзімі:</strong> 9 сынып негізінде – 3 жыл 10 ай</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-users"></i>
                <p><strong>Оқу формасы:</strong> Күндізгі</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-globe"></i>
                <p><strong>Оқыту тілі:</strong> Қазақ тілі, орыс тілі</p>
            </div>
        `
    },
    machinery: {
        title: "МАШИНАЛАР МЕН ЖАБДЫҚТАРДЫ ПАЙДАЛАНУ ЖӘНЕ ТЕХНИКАЛЫҚ ҚЫЗМЕТ КӨРСЕТУ",
        subtitle: "ТЕХНИК-МЕХАНИК",
        description: `
            <p>Машиналар мен жабдықтарды пайдалану және техникалық қызмет көрсету мамандығы бойынша білім алушыларға өнеркәсіптік жабдықтарды басқару, жөндеу және техникалық қызмет көрсету сияқты дағдыларды үйретуге бағытталған. Олар машиналарды диагностикалау, техникалық қызмет көрсету және жөндеу сияқты тапсырмаларды орындай алады.</p>
            <p>Оқу барысында студенттер механикалық жүйелермен және заманауи жабдықтармен жұмыс істеуді үйренеді. Бұл мамандық өнеркәсіп саласында сұранысқа ие.</p>
        `,
        details: `
            <div class="detail-item">
                <i class="fas fa-book"></i>
                <p><strong>Мамандық:</strong> 07151100 «МАШИНАЛАР МЕН ЖАБДЫҚТАРДЫ ПАЙДАЛАНУ ЖӘНЕ ТЕХНИКАЛЫҚ ҚЫЗМЕТ КӨРСЕТУ»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-certificate"></i>
                <p><strong>Квалификация:</strong> 4507151101 «Техник-механик»</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-clock"></i>
                <p><strong>Оқу мерзімі:</strong> 9 сынып негізінде – 3 жыл 10 ай</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-users"></i>
                <p><strong>Оқу формасы:</strong> Күндізгі</p>
            </div>
            <div class="detail-item">
                <i class="fas fa-globe"></i>
                <p><strong>Оқыту тілі:</strong> Қазақ тілі, орыс тілі</p>
            </div>
        `
    },

};
 


// Получаем элементы модального окна
const specialtyPopup = document.getElementById('specialtyPopup');
const specialtyTitle = document.getElementById('specialtyTitle');
const specialtySubtitle = document.getElementById('specialtySubtitle');
const specialtyDescription = document.getElementById('specialtyDescription');
const specialtyDetails = document.getElementById('specialtyDetails');
const closeBtn = document.querySelector('.specialtyPopup-close');
const specialtyButtons = document.querySelectorAll('.specialty-btn');

// Открытие модального окна
specialtyButtons.forEach(button => {
    button.addEventListener('click', () => {
        const specialtyKey = button.getAttribute('data-specialty');
        const specialty = specialties[specialtyKey];

        if (specialty) {
            specialtyTitle.textContent = specialty.title;
            specialtySubtitle.textContent = specialty.subtitle;
            specialtyDescription.innerHTML = specialty.description;
            specialtyDetails.innerHTML = specialty.details;
            specialtyPopup.style.display = 'block';
        }
    });
});

// Закрытие модального окна при клике на крестик
closeBtn.addEventListener('click', () => {
    specialtyPopup.style.display = 'none';
});

// Закрытие модального окна при клике вне контента
window.addEventListener('click', (event) => {
    if (event.target === specialtyPopup) {
        specialtyPopup.style.display = 'none';
    }
});