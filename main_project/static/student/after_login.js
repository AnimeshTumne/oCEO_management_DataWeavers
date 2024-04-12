// document.addEventListener("DOMContentLoaded", function() {
//     const buttons = document.querySelectorAll('.btn');
//     buttons.forEach(button => {
//         button.addEventListener('mouseover', () => {
//             button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
//         });
//         button.addEventListener('mouseout', () => {
//             button.style.boxShadow = 'none';
//         });
//     });
// });


// document.addEventListener("DOMContentLoaded", function() {
//     const buttons = document.querySelectorAll('.btn');
//     const form = document.querySelector('form');

//     buttons.forEach(button => {
//         button.addEventListener('mouseover', () => {
//             button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
//         });
//         button.addEventListener('mouseout', () => {
//             button.style.boxShadow = 'none';
//         });
//         button.addEventListener('click', function(event) {
//             event.preventDefault();  // Prevent the form from submitting immediately
//             form.style.opacity = '0'; // Trigger fade out
//             form.style.transition = 'opacity 0.5s ease-out';

//             setTimeout(function() {
//                 form.submit();  // Submit the form after the fade-out completes
//             }, 500);  // Delay matches the transition time
//         });
//     });
// });

document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.btn');
    const form = document.querySelector('form');
    // const container = document.querySelector('.container');

    // form.style.opacity = '1';  // Ensure form is visible
    // container.style.opacity = '1';  // Ensure container is visible

    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
        });
        button.addEventListener('mouseout', () => {
            button.style.boxShadow = 'none';
        });
        button.addEventListener('click', function(event) {
            event.preventDefault();  // Prevent the form from submitting immediately
            form.style.opacity = '0'; // Trigger fade out
            form.style.transition = 'opacity 0.15s ease-out';

            setTimeout(function() {
                // Create a hidden input to store the value of the clicked button
                let hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'submit_button';
                hiddenInput.value = button.value;
                form.appendChild(hiddenInput);

                form.submit();  // Submit the form after the fade-out completes
            }, 150);  // Delay matches the transition time
        });
    });
});
