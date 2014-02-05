'use strict';

/* ChapStream services defined here. */

angular.module('ChapStreamServices', []).factory('InitService', function() {
    return {
        realtime: function() {
            console.log("I am ready to fetch realtime data.");
            var ws = new WebSocket("ws://127.0.0.1:8080/timeline-socket");
            ws.open = function() {
                console.log('actim');
            };

            ws.onmessage = function(e) {
                var data = jQuery.parseJSON(e.data);
                $("#new-post").trigger("new_post_event", {new_entry: data});
            }
        }
    }
});