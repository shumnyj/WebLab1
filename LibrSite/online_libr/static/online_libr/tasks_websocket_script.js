// const roomName = JSON.parse(document.getElementById('room-name').textContent);
const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/tasks/'
);
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const table = document.querySelector('#tasks-table')
    var new_row = document.createElement("TR");
    // var col = document.createElement("TD");
    // col.innerHTML = data.task;
    // new_row.appendChild(col);
    for (var key in data)
        if(data[key])
            new_row.innerHTML +=  "<td>" + data[key] + "</td>"
        else
            new_row.innerHTML +=  "<td></td>"
    table.insertBefore(new_row, table.insertBefore(new_row, table.childNodes[2]));
    // document.querySelector('#chat-log').value += (data.task + '-' + data.task_id + '-' + data.args + '-' + data.result + '-' + data.finished + '-' + data.note + '\n');
};
/* chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};*/
