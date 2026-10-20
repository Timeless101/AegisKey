const form = document.querySelector(".authentication")

form.addEventListener("submit", (event) => {
event.preventDefault();
console.log("Form submitted");
});

const email = document.querySelector("#email_input").value;
console.log(email);