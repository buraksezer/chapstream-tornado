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
        $scope.showForm = true;
        $http.get('/api/timeline/load-timeline').success(
            function(data, status) {
                if (data.status == "OK") {
                    $scope.safeApply(function() {
                        $scope.posts = data.posts;

                    });
                }
            }
        );
    }
]);

ChapStreamControllers.controller('ProfileCtrl', ['$scope', '$http', '$routeParams',
    function ProfileCtrl($scope, $http, $routeParams) {
        $http.get('/api/user/'+$routeParams.username).success(
            function(data) {
                if (data.status == "OK") {
                    $scope.safeApply(function() {
                        $scope.user = data.user;
                        $scope.posts = data.posts;
                    });
                }
            }
        );
    }
]);

ChapStreamControllers.controller('CommentCtrl', ['$scope', '$http',
    function TimelineCtrl($scope, $http) {

    }
]);

ChapStreamControllers.controller('GroupCtrl', ['$scope', '$http', '$routeParams',
    function GroupCtrl($scope, $http, $routeParams) {
        $http.get('/api/group/'+$routeParams.group_id).success(
            function(data) {
                if (data.status == "OK") {
                    $scope.safeApply(function() {
                        $scope.group = data.group;
                        $scope.posts = data.posts;
                        if ($scope.group.subscriber_count > 1)
                            $scope.group.subscriber_clause = "subscribers";
                        else
                            $scope.group.subscriber_clause = "subscriber";

                    });
                }
            }
        );
    }
]);
