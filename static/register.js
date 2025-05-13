document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.container');
    const userData = [];
    const dataEl = [];

    dataEl.push(formEl.querySelector('input[name="fio"]'));
    dataEl.push(formEl.querySelector('input[name="group"]'));
    dataEl.push(formEl.querySelector('input[name="pswd"]'));
    dataEl.push(formEl.querySelector('input[name="submit-pswd"]'));

    formEl.addEventListener('submit', async (event) => {
        try {
            event.preventDefault();
            for (let i = 0; i < 4; i++) {
                userData.push(dataEl[i].value);
                dataEl[i].value = "";
            }

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
                window.location.href = '/sign_in';
            }

            console.log(userData);
            setTimeout(() => {window.location.href = '/sign_in';}, 2000);
        }
        catch (e) {
            console.log(e);
        }
    });
});