'use strict';

/* Directives */

var ChapStreamDirectives = angular.module('ChapStreamDirectives', []);

ChapStreamDirectives.directive('sendPost', function($http) {
    return {
        restrict: 'A',
        scope: {
            inProgress: '='
        },
        link: function (scope, elem, element) {
            elem.bind('click', function (e) {
                scope.inProgress = true;
                var form = $("#post-form")
                var post = form.val().trim();
                $http.post('/api/timeline/send-post', {body: post}).success(
                    function(data, status) {
                        if (status === 200){
                            form.val('');
                            form.trigger('autosize.resize');
                            /* This should be a constant value */
                            scope.$parent.restCharCount = 2000;
                        }
                    }
                );
            });
        }
    };
});

ChapStreamDirectives.directive('autosize', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                elem.autosize();
            });
        }
    }
});

ChapStreamDirectives.directive('countChar', function($http) {
    return {
        link: function(scope, element, attrs) {
            scope.maxCharCount = 2000;
            scope.restCharCount = 2000;
            $(element).bind("keypress keyup keydown paste", function(event) {
                if (typeof scope.commentContent == 'undefined') return;
                if (scope.restCharCount <= 0) {
                    event.preventDefault();
                } else {
                    scope.safeApply(function() {
                        scope.restCharCount = scope.maxCharCount - scope.commentContent.length;
                    })
                }
            });
        }
    };
});

ChapStreamDirectives.directive('catchNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('new_post_event', function(e, data) {
                scope.safeApply(function() {
                    scope.$parent.posts.unshift(data)
                });
            });
        }
    }
});

ChapStreamDirectives.directive('countNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            scope.new_post_count = 0;
            elem.bind('new_post_event', function(e) {
                scope.safeApply(function() {
                    scope.new_post_count += 1;
                });
            });
        }
    }
});


ChapStreamDirectives.directive('calcFromNow', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            attrs.$observe('ts', function(ts) {
                console.log(ts);
                function calcTime(timestamp) {
                    scope.safeApply(function() {
                        scope.created_at = moment.unix(parseInt(ts, 10)).format('MMMM Do YYYY, h:mm:ss a');
                        scope.calcTime = moment.unix(parseInt(ts, 10)).fromNow();
                    });
                }
                calcTime(ts);
                $timeout(function calcTimeInterval(){
                    calcTime(ts);
                    $timeout(calcTimeInterval, 60000);
                },60000);
            });
        }
    }
});

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