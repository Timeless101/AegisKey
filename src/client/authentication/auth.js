async function get_user_input(event) {
    event.preventDefault()

    let email_from_user = document.getElementById("email_input").value;
    let pwd_from_user = document.getElementById("pwd_input").value;

   await fetch("http://127.0.0.1:8000/hello")
   .then(response => response.json())
   .then(data => console.log(data))
}
