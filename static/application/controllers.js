'use strict';

/* Controllers */

var ChapStreamControllers = angular.module('ChapStreamControllers', []);

ChapStreamControllers.controller('ContentCtrl', ['$scope', '$http',
  function ContentCtrl($scope, $http) {
    console.log("This is your home page.");
  }]);


ChapStreamControllers.controller('TimelineCtrl', ['$scope', '$http',
  function TimelineCtrl($scope, $http) {
    $http.get('/load-timeline').success(
        function(data, status) {
            $scope.safeApply(function() {
                $scope.posts = data;
            });
        }
    );
  }

]);