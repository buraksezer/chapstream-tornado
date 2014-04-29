/* Directives for groups */
ChapStreamDirectives.directive('groupSubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.post("/api/group/subscribe/"+$routeParams.group_id).success(
                    function(data) {
                        scope.safeApply(function() {
                            scope.group.subscribed = true;
                            scope.group.subscriber_count++;
                        });
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('groupUnsubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.delete("/api/group/subscribe/"+$routeParams.group_id).success(
                    function(data) {
                        scope.safeApply(function() {
                            scope.group.subscribed = false;
                            scope.group.subscriber_count--;
                        });
                    }
                );
            });
        }
    }
});