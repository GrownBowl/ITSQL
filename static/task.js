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

            if (sqlRequest === null) {
                throw new error ('Поле для ввода пусто');
            }

            const response = await fetch("/go_query", {
                method: "GET",
                body: JSON.stringify({
                    request: sqlRequest,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                },
            });

            const data = await response.json();
            const tableEl = formEl.querySelector('table');

            if (data.error) {
                throw new Error ('error' + data.error);
            } else {
                const html = `<table class = check_table> 
                <tbody>
                `;
                for (const values of data){
                    html += `<tr>`
                    for (const value of values){
                        html += `
                            <td>${ value }</td>
                        `
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

    nextTaskEl.addEventListener('click', (event) => {
        event.preventDefault();
        changeTask(1, tasks);
    }); 


    previousTaskEl.addEventListener('click', (event) => {
        event.preventDefault();
        changeTask(-1, tasks);
    }); 


    async function fetchTask() {
        const response = await fetch('/get_tasks');
        const json = await response.json();
        return json;
    }

    function showTask(tasks) {
        const textTask = formEl.querySelector('text=["task"]');
        let currTask = sessionStorage.getItem("currentTask");
        textTask.innerHTML = tasks.text[currTask];
        console.log(tasks.text[currTask]);
    }

    function changeTask(direction, tasks) {
        const currTask = sessionStorage.getItem("currentTask");
        currTask += direction;

        if (currTask < 0 || currTask > 4) {
            return;
        } else {
            sessionStorage.setItem(currTask);
            showTask(tasks);
        }
    }

    /*
    function toHTML (data) {
        const fetchData = [];
        if (data.hasOwnProperty('text')){
            for(const json in data) {
                fetchData.push(json);
            }
        }
        if (data.hasOwnProperty(''))
    }
    */
});