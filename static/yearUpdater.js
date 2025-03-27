document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch("/api/year");
        const data = await response.json();
        document.getElementById("copyright-year").textContent = `©1940-${data.year}`;
    } catch (error) {
        console.error("Ошибка загрузки года:", error);
    }
});
