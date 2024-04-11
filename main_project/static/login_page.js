function validateForm() {
    var username = document.getElementById("username").value.trim();
    var password = document.getElementById("password").value.trim();

    // Check if username and password are empty
    if (username === "" || password === "") {
        alert("Please enter both username and password");
        return false;
    }

    // Add code here to authenticate the user from the database
    // If the user is authenticated, redirect to the dashboard
    // For now, we'll just return true to allow form submission
    return true;
}

function togglePasswordVisibility(inputId) {
    var passwordInput = document.getElementById(inputId);
    var toggleIcon = passwordInput.nextElementSibling;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.textContent = "hide";
    } else {
        passwordInput.type = "password";
        toggleIcon.textContent = "show";
    }
}

function toggleSubmitButton() {
    var username = document.getElementById("username").value.trim();
    var password = document.getElementById("password").value.trim();
    var submitButton = document.getElementById("submit-btn");

    if (username && password) {
        submitButton.classList.add("enabled");
    } else {
        submitButton.classList.remove("enabled");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var inputFields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    inputFields.forEach(function(field) {
        field.addEventListener("input", toggleSubmitButton);
    });
});