'use strict';

/* App Module */

var app = angular.module('ChapStream', [
  'ngRoute',
  'ChapStreamControllers',
  'ChapStreamDirectives'
]);

app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
        when('/', {
            templateUrl: '/static/application/templates/content.html',
            controller: 'ContentCtrl'
        });
    }
    ]).
    config(['$httpProvider',
        function($httpProvider) {
            console.log("burda");
            var _xsrf = $('input[name=_xsrf]').val();
            $httpProvider.defaults.headers.post['X-CSRFToken'] = _xsrf;
        }
    ]);