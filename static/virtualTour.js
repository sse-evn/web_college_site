document.getElementById("openModal").addEventListener("click", function () {
    document.getElementById("modal").style.opacity = "1";
    document.getElementById("modal").style.visibility = "visible";
});

document.getElementById("closeModal").addEventListener("click", function () {
    document.getElementById("modal").style.opacity = "0";
    document.getElementById("modal").style.visibility = "hidden";
});
