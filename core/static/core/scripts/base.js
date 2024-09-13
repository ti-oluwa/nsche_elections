const dropdownNavButton = document.querySelector('header nav #dropdown-btn');
const dropdownNav = document.querySelector('header #dropdown-nav');

dropdownNavButton.addEventListener('click', () => {
    dropdownNav.classList.toggle('show-block');
});

document.addEventListener('click', (e) => {
    if (!dropdownNav.contains(e.target) && !dropdownNavButton.contains(e.target)) {
        dropdownNav.classList.remove('show-block');
    }
});
