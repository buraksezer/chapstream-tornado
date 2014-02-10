'use strict';

/* Controllers */

var ChapStreamControllers = angular.module('ChapStreamControllers', []);

ChapStreamControllers.controller('ContentCtrl', ['$scope', '$http',
    function ContentCtrl($scope, $http) {
        console.log("This is your home page.");
    }
]);


ChapStreamControllers.controller('TimelineCtrl', ['$scope', '$http',
    function TimelineCtrl($scope, $http) {
        $http.get('/api/timeline/load-timeline').success(
            function(data, status) {
                $scope.safeApply(function() {
                    $scope.posts = data;
                });
            }
        );
    }
]);


ChapStreamControllers.controller('ProfileCtrl', ['$scope', '$http', '$routeParams',
    function ProfileCtrl($scope, $http, $routeParams) {
        $http.get('/api/user/'+$routeParams.username).success(
            function(data) {
                $scope.safeApply(function() {
                    $scope.posts = data;
                    $scope.username = $routeParams.username;
                });
            }
        );
    }
]);