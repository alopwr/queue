ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/ws/teacher/");

function deep_link(data) {
    return `https://teams.microsoft.com/l/chat/0/0?users=${teacher_principal_name},${data.principal_name},`
}

socket.onmessage = function (message) {
    var data = JSON.parse(message.data);
    switch (data['msg_type']) {
        case "queue.ticket_appended":
            if (queue_length === 0) window.location.reload();
            else if (queue_length < 4)
                $(".js-list").append("<li class=\"list-group-item  d-flex justify-content-between align-items-center\">" + data['display_name'] + "<a href=\"" + deep_link(data) + "\" target=\"_blank\" style=\"margin-left:50px\"><i class=\"far fa-comment-dots fa-lg\"></i></a></li>");
            else if (queue_length === 4)
                $(".js-list").first().find("li").last().replaceWith(`<li class=\"list-group-item\">... i <b><span class=\"js-length-3\">${queue_length + 1 - 3}</span></b> więcej</li>`);
            else
                $(".js-length-3").html(queue_length + 1 - 3);
            queue_length++;
            $(".js-length").html(queue_length);
            break;
        case 'queue.reload':
        case 'queue.ticket_deleted':
            window.location.reload();
            break;
        default:
            console.warn("Unknown websocket message:");
    }
};

