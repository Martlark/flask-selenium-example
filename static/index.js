setInterval(() => {
    const paused = document.getElementById("pause").checked;
    if (!paused)
        window.location.reload();
}, 5000);