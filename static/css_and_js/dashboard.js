const male = document.querySelector(".male");
const female = document.querySelector(".female");
const come_on_edit = document.querySelectorAll(".come-on-edit");
const go_on_edit = document.querySelectorAll(".go-on-edit");
const edit = document.querySelector(".edit");

const avatarImg = document.getElementById("avatar");
const avatarInput = document.getElementById("avatar_path");

// Update these paths to match your actual avatar image locations in static/images
const MALE_AVATAR = "/static/images/male.png";
const FEMALE_AVATAR = "/static/images/female.png";

function selectGender(selected, unselected, avatarPath) {
    // Style active/inactive buttons
    selected.style.backgroundColor = "rgb(0, 153, 255)";
    selected.style.color = "white";
    unselected.style.backgroundColor = "white";
    unselected.style.color = "rgb(0, 153, 255)";

    // Update avatar image display & hidden form input
    avatarImg.src = avatarPath;
    avatarInput.value = avatarPath;
}

male.addEventListener("click", () => selectGender(male, female, MALE_AVATAR));
female.addEventListener("click", () => selectGender(female, male, FEMALE_AVATAR));

let editing = false;

edit.addEventListener("click", () => {
    if (!editing) {
        come_on_edit.forEach(el => el.style.display = "flex");
        go_on_edit.forEach(el => el.style.display = "none");
        edit.innerHTML = '<ion-icon name="close-outline"></ion-icon><span>Cancel</span>';
        editing = true;
    } else {
        come_on_edit.forEach(el => el.style.display = "none");
        go_on_edit.forEach(el => el.style.display = "inline-block");
        edit.innerHTML = '<ion-icon name="create-outline"></ion-icon><span>Edit</span>';
        editing = false;
    }
});