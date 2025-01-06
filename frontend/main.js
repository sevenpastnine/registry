import 'htmx.org'

import hyperscript from 'hyperscript.org'
hyperscript.browserInit()

import './styles/main.sass'

// Main menu on mobile

(() => {
    const mainMenu = document.getElementById('main-menu-mobile');
    const menuOpen = document.getElementById('main-menu-mobile-open');
    const menuClose = document.getElementById('main-menu-mobile-close');

    if (menuOpen && menuClose && mainMenu) {
        menuOpen.addEventListener('click', function () {
            mainMenu.classList.toggle('hidden');
            menuOpen.classList.toggle('hidden');
            menuClose.classList.toggle('hidden');
            document.body.classList.toggle('overflow-hidden');
        });
        menuClose.addEventListener('click', function () {
            mainMenu.classList.toggle('hidden');
            menuOpen.classList.toggle('hidden');
            menuClose.classList.toggle('hidden');
            document.body.classList.toggle('overflow-hidden');
        });
    }
})();
