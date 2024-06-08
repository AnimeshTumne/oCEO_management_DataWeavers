function validateForm() {   
    var useremail = document.getElementById("username").value.trim();
    var password = document.getElementById("password").value.trim();

    // Check if username and password are empty
    if (useremail === "" || password === "") {
        alert("Please enter both username and password");
        return false;
    }

    // check if email is valid
    if (!useremail.includes("@")) {
        alert("Please enter a valid email address");
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
        // toggleIcon.textContent = "hide";
        toggleIcon.innerHTML = '<img src="../static/eye_close.png" alt="hide" class="eye-icon" id="hide-password-icon">';
    } else {
        passwordInput.type = "password";
        // toggleIcon.textContent = "show";
        toggleIcon.innerHTML = '<img src="../static/eye_open.png" alt="show" class="eye-icon" id="show-password-icon">';
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

// function toggleDarkMode() {
//     document.body.classList.toggle('dark-mode');
//   }  

function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');
  
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (body.classList.contains('dark-mode')) {
      darkModeToggle.textContent = 'Toggle Light Mode';
    } else {
      darkModeToggle.textContent = 'Toggle Dark Mode';
    }
  }

document.addEventListener("DOMContentLoaded", function() {
    var inputFields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    inputFields.forEach(function(field) {
        field.addEventListener("input", toggleSubmitButton);
    });
});