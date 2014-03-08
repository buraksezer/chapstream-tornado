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
        $http.get('/api/comment/'+$scope.$parent.post.post_id).success(
            function(data, status) {
                if (data.status == "OK") {
                    $scope.safeApply(function() {
                        $scope.$parent.post.comments = data.comments;
                        $scope.$parent.post.more_comment_count = data.count;
                    });
                }
            }
        );
    }
]);