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
                $http.post('/api/timeline/post?receiver_groups=1', {body: post}).success(
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
            console.log(elem);
            elem.bind('focusin', function(e) {
                console.log(e);
                $("#post-form").autosize({className: 'post-box', append: "\n\n\n"});
                scope.placeholder = $("#post-form").attr("placeholder");
                $("#post-form").attr("placeholder", "");
                $('.post-form-control').css('display', 'block');
                $("#chapstream-timeline form .receivers").css('display', 'block');

            });
            elem.bind('focusout', function(e) {
                console.log(e.target);
                /*if (scope.restCharCount === 2000) {
                    $('#post-form').trigger('autosize.destroy');
                    $("#post-form").attr('placeholder', scope.placeholder);
                    $('.post-form-control').css('display', 'none');
                    $("#chapstream-timeline form .receivers").css('display', 'none');
                }*/
            });
        }
    }
});

ChapStreamDirectives.directive('countChar', function($http) {
    return {
        link: function(scope, element, attrs) {
            scope.maxCharCount = 2000;
            scope.restCharCount = 2000;
            // Use angularjs for triggering events.
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
                if (typeof(scope.user) != 'undefined' && scope.user.name != data.name) {
                    return;
                }
                scope.safeApply(function() {
                    console.log(data);
                    console.log(scope.user);
                    console.log(scope.$parent.user);
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
                            scope.post.comments.comments.push(data.comment);
                            commentElem.val('');
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
                        console.log(scope.$parent.post);
                        if (data.status == "OK") {
                            scope.safeApply(function() {
                                scope.$parent.post.comments.comments = [];
                                scope.$parent.post.comments.comments = data.comments;
                                scope.$parent.post.comments.count = undefined;
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
                            scope.posts[index].comments.comments.push(data);
                            break;
                        }
                    }
                });
            });
        }
    }
});

ChapStreamDirectives.directive('editComment', function($http, $compile) {
    return {
        link: function(scope, elem, element) {
            var template = '<div class="comment-edit-box"> \
                    <form role="form">\
                        <textarea class="comment-form form-control" rows="1" count-char ng-model="commentContent" autosize-comment></textarea> \
                        <div class="comment-form-control"> \
                            <a class="comment-cancel pull-right" href="#" comment-cancel>Cancel</a> \
                            <button type="submit" class="pull-right btn btn-primary btn-xs" post-comment>Done</button> \
                            <span class="pull-left comment-char-count">{{ restCharCount }}</span> \
                        </div> \
                    </form> \
                </div>';
            elem.bind('click', function(e, data) {
                scope.safeApply(function() {
                    scope.commentContent = scope.comment.body;
                    var comment_item = $(elem).closest(".comment");
                    var comment_edit_form = comment_item.find(".comment-edit-form");
                    comment_item.find(".comment-content").hide();
                    comment_edit_form.html(template).show();
                    $compile(comment_edit_form.contents())(scope);
                    comment_edit_form.find("textarea.comment-form").trigger("focusin");
                    comment_edit_form.find("textarea.comment-form").trigger("keyup");
                });
            });
        }
    }
});

ChapStreamDirectives.directive('deleteComment', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                console.log(scope);
            });
        }
    }
});

/* Like related directives */
ChapStreamDirectives.directive('likePost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.post("/api/like/"+scope.post.post_id).success(
                    function(data) {
                        if (data.status === "OK") {
                            scope.safeApply(function() {
                                scope.post.users_liked.liked = true;
                            });
                        }
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('unlikePost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.delete("/api/like/"+scope.post.post_id).success(
                    function(data) {
                        if (data.status === "OK") {
                            console.log("unlike etti.")
                            scope.safeApply(function() {
                                scope.post.users_liked.liked = false;
                            });
                        }
                    }
                );
            });
        }
    }
});


ChapStreamDirectives.directive('catchNewLike', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind("new_like_event", function(e, data) {
                var length = scope.post.users_liked.users.length;
                for (var i=0; i<length; i++) {
                    if (scope.post.users_liked.users[i].name === data.name)
                        return;
                }
                scope.safeApply(function() {
                    scope.post.users_liked.count++;
                    var item = {"name": data.name, "screen_name": data.screen_name};
                    scope.post.users_liked.users.push(item);
                });
            });
        }
    }
});


/* Directives for groups */
ChapStreamDirectives.directive('groupSubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                console.log($routeParams.group_id);
                $http.post("/api/group/subscribe/"+$routeParams.group_id).success(
                    function(data) {
                        scope.safeApply(function() {
                            scope.group.subscribed = true;
                            scope.group.subscriber_count++;
                        });
                        console.log(scope.group);
                        console.log(data);
                    }
                );
            });
        }
    }
});

ChapStreamDirectives.directive('groupUnsubscribe', function($http, $routeParams) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                $http.delete("/api/group/subscribe/"+$routeParams.group_id).success(
                    function(data) {
                        scope.safeApply(function() {
                            scope.group.subscribed = false;
                            scope.group.subscriber_count--;
                        });
                    }
                );
            });
        }
    }
});