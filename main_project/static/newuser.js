function validateForm() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirmPassword").value;

    // Check if password and confirm password match
    if (password !== confirmPassword) {
        alert("Password and Confirm Password do not match.");
        return false;
    }

    // Check if password meets the requirements
    // var passwordRegex = /^(?=.[!@#$%^&*_-])[a-zA-Z0-9!@#$%^&*]{8,}$/;
    // var passwordRegex = /^(?=.*[!@#$%^&*=_-])(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d!@#$%^&*]{8,}$/;
    // var passwordRegex = /^(?=.*[!@#$%^&*=_-])(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d!@#$%^&*]{8,}$/;
    var passwordRegex = /^(?=.*[!@#$%^&*()-_=+[\]{};:'",.<>/?]).{8,}$/;
    if (!passwordRegex.test(password)) {
        // alert("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character (!, @, #, $, %, ^, &, *, _, -).");
        alert("Password must be at least 8 characters long and contain at least one special character (!, @, #, $, %, ^, &, *).");
        return false;
    }

    return true;
}

function toggleSubmitButton() {
    var rollNumber = document.getElementById("roll_number").value.trim();
    var firstName = document.getElementById("first_name").value.trim();
    var email = document.getElementById("email").value.trim();
    var password = document.getElementById("password").value.trim();
    var confirmPassword = document.getElementById("confirmPassword").value.trim();
    var userTypeChecked = document.querySelector('input[name="userType"]:checked');

    var submitButton = document.getElementById("submit-btn");

    if (rollNumber && firstName && email && password && confirmPassword && userTypeChecked) {
        submitButton.classList.add("enabled");
    } else {
        submitButton.classList.remove("enabled");
    }
}

function togglePasswordVisibility(inputId) {
    var passwordInput = document.getElementById(inputId);
    var toggleIcon = passwordInput.nextElementSibling;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.textContent = "hide";
        // toggleIcon.innerHTML = '<img src="{url_for("static", filename="eye_close.png")}" alt="hide">';
    } else {
        passwordInput.type = "password";
        toggleIcon.textContent = "show";
        // toggleIcon.innerHTML = '<img src="{url_for("static", filename="eye_open.png")}" alt="show">';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var inputFields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="radio"]');
    inputFields.forEach(function(field) {
        field.addEventListener("input", toggleSubmitButton);
    });
});