const socket = new WebSocket(websocketUrl)
socket.onclose = () => {window.location.reload();}
socket.onmessage = (event) => onMessage(event);

function onMessage(event){
    const data = JSON.parse(event.data)
    switch (data.type){
        case 'test':
            document.getElementById("test").innerText = data.content
    }
}

function onClickFunction(){
    window.alert("Hello");
    socket.send(JSON.stringify({type : 'test', content : 'hello from backend server'}))
}