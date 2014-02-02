var ws = new WebSocket("ws://127.0.0.1:8080/timeline-socket");
ws.open = function() {
    console.log('actim');
};

ws.onmessage = function(e) {
    alert(e.data);
}
