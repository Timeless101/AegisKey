function get_user_input(event) {
    event.preventDefault()

    let email_from_user = document.getElementById("email_input").value;
    let pwd_from_user = document.getElementById("pwd_input").value;

    console.log(email_from_user)
    console.log(pwd_from_user)
}