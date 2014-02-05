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
            elem.bind('keyup', function (e) {
                if (e.keyCode === 13) {
                    scope.inProgress = true;
                    var post = $(elem.context).val().trim();
                    $http.post('/send-post', {body: post}).success(
                        function(data, status) {
                            if (status === 200){
                                $(elem.context).val('');
                            }
                        }
                    );
                }
            });
        }
    };
});