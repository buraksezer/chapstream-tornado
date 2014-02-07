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
                $http.post('/send-post', {body: post}).success(
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