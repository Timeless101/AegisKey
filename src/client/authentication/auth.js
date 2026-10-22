function get_user_input(event) {
    event.preventDefault()

    let email_from_user = document.getElementById("email_input").value;
    let pwd_from_user = document.getElementById("pwd_input").value;

    const response = fetch("http://127.0.0.1:8000/login")
    console.log(response)

    console.log(email_from_user)
    console.log(pwd_from_user)
}
