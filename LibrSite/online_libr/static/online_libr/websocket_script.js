// const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('username-field').textContent);

const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/chat/'
);
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#chat-log').value += (data.message + '\n');
};
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();  // send on enter
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
    document.querySelector('#chat-message-input').focus();
};

document.querySelector('#chat-message-submit').onclick = function(e) {  // get text from field
    const messageInputDom = document.querySelector('#chat-message-input');
    //console.log(messageInputDom.value.length)
    if (messageInputDom.value.length > 0){
        chatSocket.send(JSON.stringify({
            'message': username + ': ' + messageInputDom.value  //  exposing user on front end is bad
        }));
        messageInputDom.value = '';
    }

    document.querySelector('#chat-message-input').focus();
};