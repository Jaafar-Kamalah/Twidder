displayView = function () {
    // the code required to display a view
    var token = localStorage.getItem("token")
    if (token == null) {
        document.getElementById("view").innerHTML = document.getElementById("welcome-view").innerHTML;
    }
    else {
        document.getElementById("view").innerHTML = document.getElementById("profile-view").innerHTML;
        // Open new websocket with server for auto-logout functionality
        let exampleSocket = new WebSocket("ws://localhost:5000/new_socket")
        exampleSocket.onopen = function() {
            exampleSocket.send(token);
          };
          exampleSocket.onmessage = function(message){
            msg = JSON.parse(message.data)
            if (msg.command== "Signed out") {
                localStorage.removeItem("token");
                localStorage.removeItem("email");
                document.getElementById("view").innerHTML = document.getElementById("welcome-view").innerHTML;
                document.getElementById("welcome-error").style.display = "block";
                document.getElementById("welcome-error-message").innerHTML = "Account has been logged in from elsewhere.";
            }
          };

        // Get user information with token to populate account information
        let request = new XMLHttpRequest();
        request.open("GET", "/get_user_data_by_token", true);
        request.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                populateAccountInformation(response.data, "account-information");
            }
        }
        request.setRequestHeader("Authorization", token);
        request.send();

         // Load messages in wall
         refreshWall();
    }

};
window.onload = function () {
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    displayView();
};

function populateAccountInformation(accountInformation, paragraphID) {
    document.getElementById(paragraphID).innerHTML = 
        "<strong>Email: </strong>" + accountInformation.email + "<br><strong>First Name: </strong>" + accountInformation.firstname + 
        "<br><strong>Family Name: </strong>" + accountInformation.familyname + "<br><strong>Gender: </strong>" + accountInformation.gender +
         "<br><strong>City: </strong>" + accountInformation.city + "<br><strong>Country: </strong>" + accountInformation.country;
}

function Login(formData) {
    let loginData ={
        username: formData["login-email"].value,
        password: formData["login-password"].value
    }

    let request = new XMLHttpRequest();
    request.open("POST", "/sign_in", true);

    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.success) {

                localStorage.setItem("token", response.data);
                localStorage.setItem("email", loginData.username)
                displayView();
            }
            else {
                document.getElementById("welcome-error").style.display = "block";
                document.getElementById("welcome-error-message").innerHTML = response.message;
            }
        }
    }

    request.setRequestHeader("Content-Type","application/json;charset=UTF-8");
    request.send(JSON.stringify(loginData));
}

function Signup(formData) {
    // Password Validation
    if (formData["signup-password"].value != formData["signup-repeat-password"].value) {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = "Repeat PSW field did not match Password field.";
        return;
    }

    // Email Validation
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!pattern.test(formData["signup-email"].value)) {
        document.getElementById("welcome-error").style.display = "block";
        document.getElementById("welcome-error-message").innerHTML = "Email is not valid.";
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

    let request = new XMLHttpRequest();
    request.open("POST", "/sign_up", true);

    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.success) {
                // Object simulating formData structure
                let loginData = {
                    "login-email": { value: account.email },
                    "login-password": { value: account.password}
                };
                Login(loginData)
            }
            else {
                document.getElementById("welcome-error").style.display = "block";
                document.getElementById("welcome-error-message").innerHTML = response.message;
            }
        }
    }

    request.setRequestHeader("Content-Type","application/json;charset=UTF-8");
    request.send(JSON.stringify(account));
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

function ChangePassword(formData) {
    if (formData["change-password-new"].value != formData["change-password-repeat"].value) {
        document.getElementById("change-password-message-container").style["background-color"] = "rgb(231, 126, 126)";
        document.getElementById("change-password-message-container").style.display = "block";
        document.getElementById("change-password-message").innerHTML = "Repeat New Password field did not match New Password field. Try again.";
        return;
    }

    let request = new XMLHttpRequest();
    request.open("PUT", "/change_password", true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.success) {
                document.getElementById("change-password-message-container").style["background-color"] = "#86d876";
            }
            else {
                document.getElementById("change-password-message-container").style["background-color"] = "rgb(231, 126, 126)";
            }
            document.getElementById("change-password-message-container").style.display = "block";
            document.getElementById("change-password-message").innerHTML = response.message;
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.setRequestHeader("Content-Type","application/json;charset=UTF-8");

    let passwordData ={
        oldpassword: formData["change-password-old"].value,
        newpassword: formData["change-password-new"].value
    };
    request.send(JSON.stringify(passwordData));
}

function logout() {
    let request = new XMLHttpRequest();
    request.open("DELETE", "/sign_out", true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            localStorage.removeItem("token");
            localStorage.removeItem("email");
            displayView();
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.send();
}


function postMessage(formData) {
    if (formData.post.value == "") {
        return;
    }

    let request = new XMLHttpRequest();
    request.open("POST", "/post_message", true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            refreshWall();
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.setRequestHeader("Content-Type","application/json;charset=UTF-8");

    let postData ={
        email: localStorage.getItem("email"),
        message: formData.post.value
    };
    request.send(JSON.stringify(postData));

    // Clear the text area
    document.getElementById("post").value = "";
}

function refreshWall() {
    let request = new XMLHttpRequest();
    request.open("GET", "/get_user_messages_by_token", true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.data != null)
            {
                for (const message of response.data) {
                    document.getElementById("message-wall").innerHTML += "<hr><strong>" + message[0] + ": </strong>" + message[1];
                }
            }
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.send();

    document.getElementById("message-wall").innerHTML = "";
}

function findUser(formData) {

    let request = new XMLHttpRequest();
    request.open("GET", "/get_user_data_by_email/" + formData["user-email"].value, true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.success)
            {
                document.getElementById("user-search-error").style.display = "none";
                userData = response.data;
                document.getElementById("user-home-page").style.display = "block";
                populateAccountInformation(userData, "user-information");
                refreshOtherUserWall();
            }
            else {
                document.getElementById("user-search-error").style.display = "block";
                document.getElementById("user-search-error-message").innerHTML = response.message;
            }
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.send();

    localStorage.setItem("otherUserEmail", formData["user-email"].value);
}

function postOtherUserMessage(formData) {
    if (formData["post-other-user"].value == "") {
        return;
    }

    let request = new XMLHttpRequest();
    request.open("POST", "/post_message", true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            refreshOtherUserWall();
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.setRequestHeader("Content-Type","application/json;charset=UTF-8");

    let postData ={
        email: localStorage.getItem("otherUserEmail"),
        message: formData["post-other-user"].value
    };
    request.send(JSON.stringify(postData));

    // Clear the text area
    document.getElementById("post-other-user").value = "";
}

function refreshOtherUserWall() {
    let request = new XMLHttpRequest();
    request.open("GET", "/get_user_messages_by_email/" + localStorage.getItem("otherUserEmail"), true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response.data != null)
            {
                for (const message of response.data) {
                    document.getElementById("other-user-message-wall").innerHTML += "<hr><strong>" + message[0] + ": </strong>" + message[1];
                }
            }
        }
    }
    request.setRequestHeader("Authorization", localStorage.getItem("token"));
    request.send();

    document.getElementById("other-user-message-wall").innerHTML = "";
}