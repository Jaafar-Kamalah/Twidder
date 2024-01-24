displayView = function () {
    // the code required to display a view
    var token = localStorage.getItem("token")
    if (token == null) {
        document.getElementById("view").innerHTML = document.getElementById("welcome-view").innerHTML;
    }
    else {
        document.getElementById("view").innerHTML = document.getElementById("profile-view").innerHTML;
    }

};
window.onload = function () {
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    displayView();
};

function validateLogin(formData) {
    var email = formData["login-email"].value;
    var password = formData["login-password"].value;
    let loginResult = serverstub.signIn(email, password);

    if (loginResult.success) {
        localStorage.setItem("token", loginResult.data)
        displayView();
    }
    else {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = loginResult.message;
    }
}

function validateSignup(formData) {
    // Password Validation
    if (formData["signup-password"].value != formData["signup-repeat-password"].value) {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = "Repeat PSW field did not match Password field. Try again.";
        return;
    }

    // Parse data from form into an object
    var account = {
        email: formData["signup-email"].value,
        password: formData["signup-password"].value,
        firstname: formData["first-name"].value,
        familyname: formData["family-name"].value,
        gender: formData["gender"].value,
        city: formData["city"].value,
        country: formData["country"].value
    };

    console.log(account);

    var signupResult = serverstub.signUp(account);

    if (signupResult.success) {
        let loginResult = serverstub.signIn(account.email, account.password);
        localStorage.setItem("token", loginResult.data)
        displayView();
    }
    else {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = signupResult.message;
    }
}

function selectTab(selected) {
    // Clear highlighting from all tabs
    tabs = document.getElementsByClassName("tab");
    for (const tab of tabs) {
        tab.style.border = "0";
        tab.style.color = "black";
    }

    // Highlight selected tab
    document.getElementById(selected + "-tab").style["border-bottom"] = "4px solid #1877f2";
    document.getElementById(selected + "-tab").style["color"] = "#1877f2";

    // Hide all panels
    panels = document.getElementsByClassName("panel");
    for (const panel of panels) {
        panel.style.display = "none";
    }

    // Show selected panel
    document.getElementById(selected + "-panel").style.display = "block";
}

function validateChangePassword(formData) {
    if (formData["change-password-new"].value != formData["change-password-repeat"].value) {
        document.getElementById("change-password-message-container").style["background-color"] = "rgb(231, 126, 126)";
        document.getElementById("change-password-message-container").style.display = "block";
        document.getElementById("change-password-message").innerHTML = "Repeat New Password field did not match New Password field. Try again.";
        return;
    }

    let changePasswordResult = serverstub.changePassword(localStorage.getItem("token"), formData["change-password-old"].value, formData["change-password-new"].value);
    if (changePasswordResult.success) {
        document.getElementById("change-password-message-container").style["background-color"] = "#86d876";
    }
    else {
        document.getElementById("change-password-message-container").style["background-color"] = "rgb(231, 126, 126)";
    }
    document.getElementById("change-password-message-container").style.display = "block";
    document.getElementById("change-password-message").innerHTML = changePasswordResult.message;
}


function logOut() {
    token = localStorage.getItem("token");
    serverstub.signOut(token);
    localStorage.removeItem("token");
    displayView();
}