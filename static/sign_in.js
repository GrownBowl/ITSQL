document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.container');
    const dataEl = [];

    dataEl.push(formEl.querySelector('input[name="fio"]'));
    dataEl.push(formEl.querySelector('input[name="group"]'));
    dataEl.push(formEl.querySelector('input[name="pswd"]'));

    const errorEl = formEl.querySelector(".error");
    const buttonEl = formEl.querySelector('.auth-btn');

    formEl.addEventListener('submit', async (event) => {
        try {
            event.preventDefault();
            const userData = [];
            for (let i = 0; i < 3; i++) {
                userData.push(dataEl[i].value);
            }


            const response = await fetch("/sign_in", {
                method: "POST",
                body: JSON.stringify({
                    userName: userData[0],
                    group: userData[1],
                    password: userData[2],
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                },
            });

            const data = await response.json();
            if (data.to_user) {
                throw new Error (data.error);
            } else {
                for (let i = 0; i < 3; i++) {
                    dataEl[i].value = "";
                }
                window.location.href = '/';
            }
        }
        catch (e) {
            let textError = JSON.parse(e.message);
            if (textError.to_user){
                errorEl.innerHTML = textError.to_user;
            } else {
                console.log(textError);
            }
            buttonEl.classList.remove("auth-btn");
            buttonEl.classList.add("shake");
            setTimeout(() => {
                buttonEl.classList.remove("shake");
                buttonEl.classList.add("auth-btn");
            }, 750);
            setTimeout(() => { errorEl.innerHTML = ""; }, 3000);
        }
    });
});
