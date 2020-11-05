ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/ws/students/");

socket.onmessage = function (message) {
    var data = JSON.parse(message.data);
    console.log(data);
    window.location.reload();
};