ChapStreamDirectives.directive('relationshipStatus', function($http, $routeParams) {
    return {
        link: function(scope, element, attrs) {
            $http.get("/api/user/relationship/"+$routeParams.username).success(
                function(data) {
                    scope.safeApply(function() {
                        if (data.rule === null) {
                            scope.relSubsAndBan = true;
                        } else if (data.rule === "BANNED") {
                            scope.relUnban = true;
                        } else if (data.rule === "SUBSCRIBED") {
                            scope.relUnsubsAndBan = true;
                        } else if (data.rule === "YOU") {
                            scope.my_profile = true;
                        }
                    });
                }
            );
        }
    }
});

ChapStreamDirectives.directive('subscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.post("/api/user/subscribe/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = false;
                                scope.$parent.relUnsubsAndBan = true;
                            });
                        }
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('unsubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.delete("/api/user/unsubscribe/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relSubsAndBan = true;
                            });
                        }
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('block', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.post("/api/user/block/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = false;
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relUnban = true;
                            });
                        }
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('unblock', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.delete("/api/user/unblock/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = true;
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relUnban = false;
                            });
                        }
                    }
                );
            });
        }
    }
});
