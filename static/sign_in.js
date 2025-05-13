document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.container');
    const userData = [];
    const dataEl = [];

    dataEl.push(formEl.querySelector('input[name="fio"]'));
    dataEl.push(formEl.querySelector('input[name="group"]'));
    dataEl.push(formEl.querySelector('input[name="pswd"]'));

    formEl.addEventListener('submit', async (event) => {
        try {
            event.preventDefault();
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
            if (data.error) {
                throw new Error ('error' + data.error);
            } else {
                for (let i = 0; i < 3; i++) {
                    dataEl[i].value = "";
                }
                window.location.href = '/';
            }
        }
        catch (e) {
            console.log(e);
        }
    });
});