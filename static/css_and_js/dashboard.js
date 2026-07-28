// static/css_and_js/dashboard.js

const male = document.querySelector(".male");
const female = document.querySelector(".female");
const come_on_edit = document.querySelectorAll(".come-on-edit");
const go_on_edit = document.querySelectorAll(".go-on-edit");
const edit = document.querySelector(".edit");

const avatarImg = document.getElementById("avatar");
const avatarInput = document.getElementById("avatar_path");

const MALE_AVATAR = "/static/images/male.png";
const FEMALE_AVATAR = "/static/images/female.png";

function selectGender(selected, unselected, avatarPath) {
    selected.style.backgroundColor = "#0284c7";
    selected.style.color = "white";
    unselected.style.backgroundColor = "white";
    unselected.style.color = "#0284c7";

    avatarImg.src = avatarPath;
    avatarInput.value = avatarPath;
}

if (male && female) {
    male.addEventListener("click", (e) => {
        e.preventDefault();
        selectGender(male, female, MALE_AVATAR);
    });

    female.addEventListener("click", (e) => {
        e.preventDefault();
        selectGender(female, male, FEMALE_AVATAR);
    });
}

let editing = false;

edit.addEventListener("click", (e) => {
    e.preventDefault();
    if (!editing) {
        come_on_edit.forEach(el => el.style.setProperty("display", "flex", "important"));
        go_on_edit.forEach(el => el.style.setProperty("display", "none", "important"));
        edit.innerHTML = '<ion-icon name="close-outline"></ion-icon><span>Cancel</span>';
        editing = true;
    } else {
        come_on_edit.forEach(el => el.style.setProperty("display", "none", "important"));
        go_on_edit.forEach(el => el.style.setProperty("display", "inline-block", "important"));
        edit.innerHTML = '<ion-icon name="create-outline"></ion-icon><span>Edit</span>';
        editing = false;
    }
});