'use strict';

ChapStreamDirectives.directive('countChar', function($http) {
    return {
        link: function(scope, element, attrs) {
            scope.maxCharCount = 2000;
            scope.restCharCount = 2000;
            // Use angularjs for triggering events.
            $(element).bind("keypress keyup keydown paste", function(event) {
                // TODO: rename commentContent
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

ChapStreamDirectives.directive('calcFromNow', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            attrs.$observe('ts', function(ts) {
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