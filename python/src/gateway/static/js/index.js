document.addEventListener("DOMContentLoaded", function(event){
    let loginForm = document.getElementById("loginForm");
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submit();
    })
});


const submit = () => {
    let username = document.getElementById("name-login");
    let password = document.getElementById("password-login");

    // Verify regex for valid characters for username and password

    if(username.value == "" || password.value == ""){
        alert("Ensure input in both fields");
    }
    else{
        encoded = btoa(username.value + ":" + password.value);
        token = `Basic ${encoded}`;
        const response = fetch("./login", {
            method: 'POST',
            headers: {
                "Authorization" : token,
            }
        }).then(response => {
            if(response.redirected){
                window.location.href = response.url;
            }
            else{
                let message = document.getElementById("message");
                message.textContent(response.text());
                return response.text();
            }
        }).then(data => {
            console.log(data);
        }).catch(error => {
            console.error(error);
        });
    }
};

