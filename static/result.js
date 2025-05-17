document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.result-container');

    const resultEl = formEl.querySelector('.result-text');
    const buttonEl = formEl.querySelector('.exit-btn');

    resultEl.innerHTML = "Ваш результат: " + get_result();

    buttonEl.addEventListener('click', async (event) => {
        try {
            event.preventDefault();
            event.stopPropagation();

            const response = await fetch("/logout");
            const data = await response.json();

            if (data.error) {
                throw new Error("error" + data.error);
            }
       } catch (e) {
            console.log(e);
       }
    });

    async function get_result() {
        const response = await fetch('/get_result');
        const data = await response.json();
        return data;
    }
});