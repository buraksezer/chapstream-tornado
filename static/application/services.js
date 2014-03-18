'use strict';

/* ChapStream services defined here. */

angular.module('ChapStreamServices', []).factory('InitService', function() {
    return {
        realtime: function() {
            console.log("I am ready to fetch realtime data.");
            var ws = new WebSocket("ws://127.0.0.1:8000/timeline-socket");
            ws.open = function() {
                console.log('actim');
            };

            ws.onmessage = function(e) {
                var data = jQuery.parseJSON(e.data);
                if (data['TYPE'] === 'SUBSCRIPTION_NOTIFY') {
                } else if (data['type'] === 'POST') {
                    $('#new-post, #posts').trigger("new_post_event", data);
                } else if (data['type'] === 'COMMENT') {
                    $('#chapstream-timeline').trigger("new_comment_event", data);
                } else if (data['type'] === 'LIKE') {
                    $('#post-social-'+data.post_id).trigger("new_like_event", data);
                }
            }
        }
    }
});