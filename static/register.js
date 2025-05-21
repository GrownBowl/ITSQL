document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.container');
    const dataEl = [];

    dataEl.push(formEl.querySelector('input[name="fio"]'));
    dataEl.push(formEl.querySelector('input[name="group"]'));
    dataEl.push(formEl.querySelector('input[name="pswd"]'));
    dataEl.push(formEl.querySelector('input[name="submit-pswd"]'));

    const buttonEl = formEl.querySelector('.register-button');
    const errorEl = formEl.querySelector(".error");

    formEl.addEventListener('submit', async (event) => {
        try {
            const userData = [];
            event.preventDefault();
            for (let i = 0; i < 4; i++) {
                userData.push(dataEl[i].value);
            }
            errorEl.value = "";

            if (userData[2] != userData[3]) {
                throw new Error ('Пароли не совпадают.');
            }

            const response = await fetch("/register", {
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
            if (data.error) {
                throw new Error ('error' + data.error);
            } else {
                for (let i = 0; i < 4; i++) {
                    dataEl[i].value = "";
                }
                window.location.href = 'sign_in';
            }
        }
        catch (e) {
            errorEl.innerHTML = e.message;
            buttonEl.classList.remove("register-button");
            buttonEl.classList.add("shake");
            setTimeout(() => {
                buttonEl.classList.remove("shake");
                buttonEl.classList.add("register-button");
            }, 750);
            setTimeout(() => { errorEl.innerHTML = ""; }, 3000);
            console.log(e);
        }
    });
});