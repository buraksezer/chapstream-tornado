'use strict';

/* Like related directives */
ChapStreamDirectives.directive('likePost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.post("/api/like/"+scope.post.post_id).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.post.users_liked.liked = true;
                            });
                            var event_data = {"name": scope.currentUser, "screen_name": "You"}
                            $("#post-social-"+scope.post.post_id).trigger("new_like_event", event_data);
                        }
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('unlikePost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.delete("/api/like/"+scope.post.post_id).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.post.users_liked.liked = false;
                                var length = scope.post.users_liked.users.length;
                                for (var i=0; i<length; i++) {
                                    if (scope.post.users_liked.users[i].name === scope.currentUser)
                                        scope.post.users_liked.users.splice(i, 1);
                                }
                                scope.post.users_liked.count--;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('catchNewLike', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind("new_like_event", function(e, data) {
                var length = scope.post.users_liked.users.length;
                for (var i=0; i<length; i++) {
                    if (scope.post.users_liked.users[i].name === data.name)
                        return;
                }
                scope.safeApply(function() {
                    scope.post.users_liked.count++;
                    var item = {"name": data.name, "screen_name": data.screen_name};
                    scope.post.users_liked.users.push(item);
                });
            });
        }
    }
});