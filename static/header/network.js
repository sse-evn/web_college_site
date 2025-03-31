function getExternalIP() {
    // Используем сервис для определения IP
    fetch('https://api.ipify.org?format=json')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ip-address').textContent = `IP: ${data.ip}`;
        })
        .catch(error => {
            console.error('Ошибка получения IP:', error);
            document.getElementById('ip-address').textContent = 'IP: недоступен';
        });
}

// Вызываем функцию при загрузке страницы
window.addEventListener('DOMContentLoaded', getExternalIP);
