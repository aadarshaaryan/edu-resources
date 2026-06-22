let notify = document.getElementById("notify");

notify.classList.remove("notify_go");
notify.classList.add("notify_come");

setTimeout(() => {
    notify.classList.remove("notify_come");
    notify.classList.add("notify_go");
}, 6000);
