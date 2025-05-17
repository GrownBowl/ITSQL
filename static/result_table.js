document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.results-container');

    const resutlTableEl = formEl.querySelector('.results-content');
    const buttonEl = formEl.querySelector('.exit-btn')

    await toHTML(resutlTableEl);

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

    async function toHTML(selectorEl) {
        const data = await getAllResults();

        let html = '';

        html = `<div class="table-scroll">
        <table border="1" class = result_table> 
        <tbody>
        `;
        for (const values of data){
            html += `<tr><td>${ values }</td></tr>`
        }
        html += `
        </tbody>
        </table>
        </div>
        `;
        selectorEl.innerHTML = html;
    }

    async function getAllResults() {
        const response = await fetch('/get_result_table');
        const data = await response.json();
        return data;
    }
});