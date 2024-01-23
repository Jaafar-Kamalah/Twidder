displayView = function () {
    // the code required to display a view
    document.getElementById("view").innerHTML = document.getElementById("welcome-view").innerHTML;
};
window.onload = function () {
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    displayView();
};

function validateLogin(formData) {
    console.log(formData);
    alert(formData.email.value);
}

function validateSignup(formData) {
    // Password Validation
    if(formData["signup-password"].value != formData["signup-repeat-password"].value) {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = "Repeat PSW field did not match Password field. Try again.";
        return;
    }

    var email = formData["signup-email"].value;
    var password = formData["signup-password"].value;
    var firstname = formData["first-name"].value;
    var familyname = formData["family-name"].value;
    var gender = formData["gender"].value;
    var city = formData["city"].value;
    var country = formData["country"].value;

    var account = {
        email: email,
        password: password,
        firstname: firstname,
        familyname: familyname,
        gender: gender,
        city: city,
        country: country
    };

    console.log(account);

    var signupResult = serverstub.signUp(account);

    if (signupResult.success) {
        document.getElementById("view").innerHTML = document.getElementById("profile-view").innerHTML;
    }
    else {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = signupResult.message;
    }
}