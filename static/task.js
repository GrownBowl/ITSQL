document.addEventListener('DOMContentLoaded', async () => {
    const formEl = document.querySelector('.container');

    const buttonTryEl = formEl.querySelector('#buttonTry');
    const buttonSendEl = formEl.querySelector('#buttonSend');
    const sqlRequestEl = formEl.querySelector('textarea[name="sql"]')

    sessionStorage.setItem("currentTask", 0);

    const tasks = await fetchTask();
    showTask(tasks);

    buttonTryEl.addEventListener('click', async (event) => {
        try{
            event.preventDefault();
            event.stopPropagation();

            const sqlRequest = sqlRequestEl.value;
            console.log(sqlRequest);
            if (sqlRequest === null) {
                throw new error ('Поле для ввода пусто');
            }

            const response = await fetch("/go_query", {
                method: "POST",
                body: JSON.stringify({
                    request: sqlRequest,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                },
            });

            const data = await response.json();

            const tableEl = formEl.querySelector('.output');

            if (data.error) {
                throw new Error ('error' + data.error);
            } else {
                let html = '';
                console.log(data);
                html += `<table border="1" class=check_table> 
                <tbody>
                `;
                for (const values of data){
                    html += `<tr>`
                    for (const value of values) {
                        html += `<td>${value}</td>`;
                    }
                    html += `</tr>`
                }
                html += `
                </tbody>
                </table>
                `;
                tableEl.innerHTML = html;
                console.log(data);
            }

        } catch (e) {
            console.log(e);
        }
        
    });

    
    buttonSendEl.addEventListener('click', async (event) => {
        try {
            event.preventDefault();
            event.stopPropagation();

            const sqlRequest = sqlRequestEl.value;
            let currTask = sessionStorage.getItem("currentTask");

            if (sqlRequest === null) {
                throw new error ('Поле для ввода пусто');
            }

            const response = await fetch("/check_answer", {
                method: "POST",
                body: JSON.stringify({
                    request: sqlRequest,
                    number: currTask,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                },
            });
            
            const data = await response.json();

            if (data.error) {
                throw new Error ('error' + data.error);
            } else {
                sessionStorage.setItem("currentTask", currTask++);
            }
        } catch (e) {
            console.log(e);
        }
    });

    const nextTaskEl = formEl.querySelector("#next_task");
    const previousTaskEl = formEl.querySelector("#previous_task");

    nextTaskEl.addEventListener('click', async (event) => {
        event.preventDefault();
        await changeTask(1, tasks);
    }); 


    previousTaskEl.addEventListener('click', async (event) => {
        event.preventDefault();
        await changeTask(-1, tasks);
    }); 


    async function fetchTask() {
        const response = await fetch('/get_tasks');
        const json = await response.json();
        return json;
    }

    async function showTask(tasks) {
        const textTask = formEl.querySelector('.task');
        let currTask = Number(sessionStorage.getItem("currentTask"));
        textTask.innerHTML = tasks[currTask].text;

        const numberTask = formEl.querySelector('.numTask');
        numberTask.innerHTML = `Задание #${currTask+1}`;
    }

    async function changeTask(direction, tasks) {
        let currTask = Number(sessionStorage.getItem("currentTask"));
        currTask += direction;
        try {
            if (currTask < 0 || currTask > 4) {
                return;
            } else {
                sessionStorage.removeItem("currentTask");
                sessionStorage.setItem("currentTask", currTask);
                showTask(tasks);
            }
        } catch (e) {
            console.log(e);
        }
    }
});
