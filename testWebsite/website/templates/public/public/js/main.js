const chatForm = document.getElementById('chat-form');
const chatMessages = document.querySelector('.chat-messages')

//get userrname and room from URL

const { username, room } = Qs.parse(location.search, {
    ignoreQueryPrefix: true
});


const socket = io();

//join chat room
socket.emit('joinRoom', { username, room});


socket.on('message', message => {
    console.log(message);
    outputMessage(message);

    //scroll down
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

//message submit
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    //getting the msg text
    const msg = e.target.elements.msg.value;

    // emit message to the server
    socket.emit('chatMessage', msg);
    //Scroll Down
    e.target.elements.msg.value = '';
    e.target.elements.msg.focus();
});

// output message to domn
function outputMessage(message) {
    const div = document.createElement('div');
    div.classList.add('message');
    div.innerHTML = `<p class="meta">${message.username} <span> ${message.time}</span></p>
    <p class="text">
        ${message.text}
    </p>`;
    document.querySelector('.chat-messages').appendChild(div);
}