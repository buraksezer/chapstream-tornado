'use strict';

/* App Module */

var TEMPLATE_ROOT = "/static/application/templates";

var app = angular.module('ChapStream', [
    'ChapStreamServices',
    'ngRoute',
    'ChapStreamControllers',
    'ChapStreamDirectives'
]);

app.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
        when('/', {
            templateUrl: TEMPLATE_ROOT+'/content.html',
            controller: 'ContentCtrl'
        }).
        when("/:username", {
            templateUrl: TEMPLATE_ROOT+'/profile.html',
            controller: 'ProfileCtrl'
        });
    }
    ]).
    config(['$httpProvider',
        function($httpProvider) {
            var _xsrf = $('input[name=_xsrf]').val();
            /* TODO: Post seems unnecessary */
            $httpProvider.defaults.headers.post['X-CSRFToken'] = _xsrf;
            $httpProvider.defaults.headers.common['X-CSRFToken'] = _xsrf;
        }
    ]).config(["$locationProvider", function($locationProvider) {
        $locationProvider.html5Mode(true);
    }]);

app.run(function($rootScope, InitService) {
    InitService.realtime();

    /* Updates model on the fly */
    $rootScope.safeApply = function(fn) {
        var phase = this.$root.$$phase;
        if(phase == '$apply' || phase == '$digest') {
            if(fn && (typeof(fn) === 'function')) {
                fn();
            }
        } else {
            this.$apply(fn);
        }
    };
});