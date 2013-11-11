var ws = new WebSocket("ws://127.0.0.1:8888/timeline-socket");
ws.open = function() {
    ws.send("Hello, world");
};
ws.onmessage = function(e) {
    console.log(e.data);
}
