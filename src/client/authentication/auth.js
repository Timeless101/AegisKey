async function get_user_input(event) {

    let url = "http://127.0.0.1:8000/login"

    event.preventDefault()

    let email_from_user = document.getElementById("email_input").value;
    let pwd_from_user = document.getElementById("pwd_input").value;

    await fetch(url, {
    method: "POST",
    body: JSON.stringify({
        username: email_from_user,
        pwd: pwd_from_user
    })

    })

   .then(response => response.json())
   .then(data => console.log(data))
}
