function toggleMenu() {
    var sidebar = document.getElementById('sidebar');
    var mainContent = document.getElementById('main-content');
    var menuIcon = document.querySelector('.menu-icon');
	var mainContentAbove = document.getElementById('main-content-above');
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
    mainContent.classList.toggle('main-content-shift');
	mainContentAbove.classList.toggle('main-content-shift');
    // add transition effect - when clicked on anywhere in the document, sidebar should close
    document.addEventListener('click', function(event) {
        if (!event.target.closest('#sidebar') && !event.target.closest('.menu-icon')) {
            sidebar.classList.remove('open');
            menuIcon.classList.remove('open');
            mainContent.classList.remove('main-content-shift');
			mainContentAbove.classList.remove('main-content-shift');
        }
    });
}

function templateToggleMenu() {
    const sidebar = documenttemplate.getElementById('sidebar');
    sidebar.classList.toggle('show');
}
