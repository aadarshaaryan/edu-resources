let toggle = document.getElementsByClassName('toggle-dark-mode-w')[0];
let toggle_img = document.getElementsByClassName('toggle-dark-mode')[0];
let down = document.getElementsByClassName('drop-down-w')[0];

let toggled = true;
toggle.addEventListener('click', () => {
    if (toggled) {
        document.getElementsByTagName('body')[0].style.backgroundColor = "black";
        document.getElementsByTagName('body')[0].style.color = "white";
        toggled = false;
        toggle_img.src = 'static/images/day-and-night (1).png'
        toggle.style.backgroundColor = 'black'
    } else {
        document.getElementsByTagName('body')[0].style.backgroundColor = "white";
        document.getElementsByTagName('body')[0].style.color = "black";
        toggled = true;
        toggle_img.src = 'static/images/day-and-night.png'
        toggle.style.backgroundColor = 'white'
    }
})


let menu = document.getElementsByClassName('menu')[0];

menu.style.visibility = "hidden";
down.addEventListener('click', () => {
    if (menu.style.visibility == "hidden") {
        menu.style.visibility = "inherit";
        down.classList.add('dropAnime')
    } else {
        menu.style.visibility = "hidden";
        down.classList.remove('dropAnime')
    }
})


let notify = document.getElementById("notify");

notify.classList.remove("notify_go");
notify.classList.add("notify_come");

setTimeout(() => {
    notify.classList.remove("notify_come");
    notify.classList.add("notify_go");
}, 6000);
