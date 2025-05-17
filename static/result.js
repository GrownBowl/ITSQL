document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.result-container');

    const resultEl = formEl.querySelector('.result-text');
    const buttonEl = formEl.querySelector('.exit-btn');

    resultEl.innerHTML = "Ваш результат: " + await get_result();

    buttonEl.addEventListener('click', async (event) => {
        try {
            event.preventDefault();
            event.stopPropagation();

            window.location.href = "/logout";
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
