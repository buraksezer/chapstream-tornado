'use strict';

/* Directives */

var ChapStreamDirectives = angular.module('ChapStreamDirectives', []);

ChapStreamDirectives.directive('sendPost', function($http) {
    return {
        restrict: 'A',
        link: function (scope, elem, element) {
            elem.bind('click', function (e) {
                scope.inProgress = true;
                var form = $("#post-form")
                var post = form.val().trim();
                $http.post('/api/timeline/post', {body: post}).success(
                    function(data, status) {
                        if (status === 200){
                            form.val('');
                            form.trigger('autosize.destroy');
                            /* This should be a constant value */
                            scope.$parent.restCharCount = 2000;
                            scope.restCharCount = 2000;
                            form.trigger('focusout');
                        }
                    }
                );
            });
        }
    };
});

ChapStreamDirectives.directive('autosize', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('focusin', function(e) {
                elem.autosize({className: 'post-box', append: "\n\n\n"});
                scope.placeholder = element.placeholder;
                $(this).attr('placeholder','');
                $('.post-form-control').css('display', 'block');
            });
            elem.bind('focusout', function(e) {
                if (scope.restCharCount === 2000) {
                    $('#post-form').trigger('autosize.destroy');
                    $(this).attr('placeholder', scope.placeholder);
                    $('.post-form-control').css('display', 'none');
                }
            });
        }
    }
});

ChapStreamDirectives.directive('countChar', function($http) {
    return {
        link: function(scope, element, attrs) {
            scope.maxCharCount = 2000;
            scope.restCharCount = 2000;
            $(element).bind("keypress keyup keydown paste", function(event) {
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

ChapStreamDirectives.directive('catchNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('new_post_event', function(e, data) {
                scope.safeApply(function() {
                    scope.$parent.posts.unshift(data)
                });
            });
        }
    }
});

ChapStreamDirectives.directive('countNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            scope.new_post_count = 0;
            elem.bind('new_post_event', function(e) {
                scope.safeApply(function() {
                    scope.new_post_count += 1;
                });
            });
        }
    }
});


ChapStreamDirectives.directive('calcFromNow', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            attrs.$observe('ts', function(ts) {
                console.log(ts);
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

ChapStreamDirectives.directive('relationshipStatus', function($http, $routeParams) {
    return {
        link: function(scope, element, attrs) {
            $http.get("/api/user/relationship/"+$routeParams.username).success(
                function(data) {
                    scope.safeApply(function() {
                        if (data.rule === null) {
                            scope.relSubsAndBan = true;
                        } else if (data.rule === "BANNED") {
                            scope.relUnban = true;
                        } else if (data.rule === "SUBSCRIBED") {
                            scope.relUnsubsAndBan = true;
                        } else if (data.rule === "YOU") {
                            scope.my_profile = true;
                        }
                    });
                }
            );
        }
    }
});


ChapStreamDirectives.directive('subscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.post("/api/user/subscribe/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = false;
                                scope.$parent.relUnsubsAndBan = true;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('unsubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.delete("/api/user/unsubscribe/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relSubsAndBan = true;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('block', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.post("/api/user/block/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = false;
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relUnban = true;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('unblock', function($http, $routeParams) {
    return {
        link: function(scope, elem, elements) {
            elem.bind('click', function (e) {
                $http.delete("/api/user/unblock/"+$routeParams.username).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.$parent.relSubsAndBan = true;
                                scope.$parent.relUnsubsAndBan = false;
                                scope.$parent.relUnban = false;
                            });
                        }
                    }
                );
            });
        }
    }
});

/* Comment Related Directives */
ChapStreamDirectives.directive('showCommentBox', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                $(elem).closest('.post').find(".comment-box").css("display", "block");
            });
        }
    }
});

ChapStreamDirectives.directive('autosizeComment', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('focusin', function(e) {
                elem.autosize();
                scope.placeholder = element.placeholder;
                $(this).attr('placeholder','');
            });
            elem.bind('focusout', function(e) {
                if (scope.restCharCount === 2000) {
                    $('#post-form').trigger('autosize.destroy');
                    $(this).attr('placeholder', scope.placeholder);
                }
            });
        }
    }
});

ChapStreamDirectives.directive('commentCancel', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                var commentbox = $(elem).closest('.post').find(".comment-box");
                $(commentbox).css("display", "none");
            });
        }
    }
});

ChapStreamDirectives.directive('postComment', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                var commentElem = $(elem).closest('.post').find(".comment-form");
                // FIX empty commentElem
                $http.post("/api/comment/"+scope.post.post_id, {body: commentElem.val()}).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.post.comments.push(data.comment);
                            commentElem.val('');
                            console.log(data);
                            console.log($(elem).closest('.comment-form-control').find('.comment-cancel'));
                            var cancelLink = $(elem).closest('.comment-form-control').find('.comment-cancel');
                            cancelLink.trigger("click");
                        }
                    }
                );
                var commentElem = $(elem).closest('.post').find(".comment-form");
            });
        }
    }
});

ChapStreamDirectives.directive('moreComments', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                $http.get('/api/comment/'+scope.$parent.post.post_id+"/all").success(
                    function(data, status) {
                        if (data.status == "OK") {
                            scope.safeApply(function() {
                                scope.$parent.post.comments = [];
                                scope.$parent.post.comments = data.comments;
                                scope.$parent.post.more_comment_count = undefined;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('catchNewComment', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('new_comment_event', function(e, data) {
                scope.safeApply(function() {
                    var post_count = scope.posts.length;
                    for(var index=0; index<post_count; index++) {
                        if (scope.posts[index].post_id === data.post_id) {
                            scope.posts[index].comments.push(data);
                            break;
                        }
                    }
                });
            });
        }
    }
});