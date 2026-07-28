document.addEventListener("DOMContentLoaded", () => {
    const notify = document.getElementById("notify");
    if (!notify) return; // Prevents null errors if no message is flashed

    notify.classList.remove("notify_go");
    notify.classList.add("notify_come");

    setTimeout(() => {
        notify.classList.remove("notify_come");
        notify.classList.add("notify_go");

        // Wait for 300ms animation to finish, then remove from view completely
        setTimeout(() => {
            notify.style.display = "none";
            notify.remove();
        }, 300);
    }, 4000); // reduced slightly to 4s so users don't wait too long
});