'use strict';

/* App Module */

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
            templateUrl: '/static/application/templates/content.html',
            controller: 'ContentCtrl'
        });
    }
    ]).
    config(['$httpProvider',
        function($httpProvider) {
            var _xsrf = $('input[name=_xsrf]').val();
            $httpProvider.defaults.headers.post['X-CSRFToken'] = _xsrf;
        }
    ]);


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