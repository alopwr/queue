function msToTime(duration) {
    var milliseconds = parseInt((duration % 1000) / 100),
        seconds = Math.floor((duration / 1000) % 60),
        minutes = Math.floor((duration / (1000 * 60)) % 60),
        hours = Math.floor((duration / (1000 * 60 * 60)) % 24);
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;
    if (hours > 0) {
        hours = (hours < 10) ? "0" + hours : hours;
        return hours + ":" + minutes + ":" + seconds;
    } else
        return minutes + ":" + seconds;
}

function getTimerValue() {
    return msToTime(new Date() - startedAt);
}

$(document).ready(function () {
    const clock = $("#timer");
    clock.html(getTimerValue());
    setInterval(() => {
        clock.html(getTimerValue());
    }, 1000);
});