ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/ws/students/" + userId);

refresh_timer = null;

function setTimer() {
    if (refresh_timer == null)
        refresh_timer = setTimeout(function () {
            window.location.reload();
        }, 10000);
}

socket.onclose = setTimer;
socket.onerror = setTimer;

socket.onopen = function (e) {
    if (refresh_timer) {
        clearTimeout(refresh_timer);
        refresh_timer = null;
    }
    socket.send(JSON.stringify({"type": "get.update"}));
};

socket.onmessage = function (message) {
    data = JSON.parse(message.data);
    switch (data['msg_type']) {
        case 'queue.updated':
            if (data['position'] < 0) {
                window.location.reload();
            } else if (data['position'] === 0) {
                if (!$("#zero_in_queue").length)
                    window.location.reload();
            } else {
                $("span.js-position").html(data['position']);
                $("span.js-time").html(data['estimated_time']);
                document.title = "Kolejka | " + data['position'] + ". w kolejce";
            }
            break;
        case 'queue.cleared':
            window.location.replace("/?cleared=True");
            break;
        default:
            console.warn("Unknown websocket message:");
    }
};
