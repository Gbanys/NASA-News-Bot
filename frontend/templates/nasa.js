const socket = new WebSocket('{{ websocket_url }}')
socket.onclose = () => {window.location.reload();}
socket.onmessage = (event) => onMessage(event);