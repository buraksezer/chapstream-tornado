'use strict';

/* App Module */

var app = angular.module('ChapStream', [
  'ngRoute',
  'ChapStreamControllers',
]);

app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/', {
        templateUrl: '/static/application/templates/content.html',
        controller: 'ContentCtrl'
      });
  }]);