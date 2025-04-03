document.addEventListener('DOMContentLoaded', function() {
    // Загрузка статистики
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('visitors-count').textContent = data.visitors;
            document.getElementById('new-users').textContent = data.newUsers;
            document.getElementById('content-items').textContent = data.contentItems;
        });

    // Загрузка последней активности
    fetch('/admin/api/activity')
        .then(response => response.json())
        .then(data => {
            const activityList = document.getElementById('activity-list');
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.action} - ${item.timestamp}`;
                activityList.appendChild(li);
            });
        });

    // Обработчики кнопок
    document.getElementById('clear-cache').addEventListener('click', () => {
        fetch('/admin/api/clear-cache', { method: 'POST' })
            .then(() => alert('Кэш очищен'));
    });

    document.getElementById('backup-now').addEventListener('click', () => {
        fetch('/admin/api/backup', { method: 'POST' })
            .then(() => alert('Резервная копия создана'));
    });

    document.getElementById('check-updates').addEventListener('click', () => {
        fetch('/admin/api/check-updates')
            .then(response => response.json())
            .then(data => alert(data.message));
    });
});