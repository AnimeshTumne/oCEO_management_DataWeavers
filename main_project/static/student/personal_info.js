// document.addEventListener("DOMContentLoaded", function() {
//     const menuIcon = document.querySelector('.menu-icon');
//     const sidebar = document.getElementById('sidebar');
//     const mainContent = document.getElementById('main-content');

//     menuIcon.addEventListener('click', function() {
//         sidebar.classList.toggle('open');
//         mainContent.style.transition = 'margin-left 0.2s ease';
//         mainContent.classList.toggle('shift');
//     });

//     // Add fade-out effect on button click
//     const buttons = document.querySelectorAll('.update-profile');
//     buttons.forEach(button => {
//         button.addEventListener('click', function(event) {
//             event.preventDefault();
//             mainContent.style.opacity = '0';
//             mainContent.style.transition = 'opacity 0.15s ease-out';
//             setTimeout(function() {
//                 // Submit the closest form
//                 button.closest('form').submit();
//             }, 150);
//         });
//     });
// });

function toggleMenu() {
    var sidebar = document.getElementById('sidebar');
    var mainContent = document.getElementById('main-content');
    var menuIcon = document.querySelector('.menu-icon');
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
}
