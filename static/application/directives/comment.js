'use strict';

/* Comment related directives defined here */

ChapStreamDirectives.directive('commentEvents', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            var comment_edit_el = $(element).find('.comment-edit-dropdown');
            element.on('mouseenter', function() {
                $(comment_edit_el).css('display', 'inline-block');
            });
            element.on('mouseleave', function() {
                $(comment_edit_el).css('display', 'none');
            });
        }
    }
});

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
                console.log('burda');
                scope.placeholder = element.placeholder;
                $(this).attr('placeholder','');
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
                        <textarea id="comment-edit-{{ comment.id }}" class="comment-form form-control" rows="1" count-char ng-model="commentContent" autosize-comment></textarea> \
                        <div class="comment-form-control"> \
                            <a class="comment-cancel pull-right" href="#" comment-cancel>Cancel</a> \
                            <button type="submit" class="pull-right btn btn-primary btn-xs" done-comment-edit>Done</button> \
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
                });
                $('#comment-edit-'+scope.comment.id).trigger('focusin');
            });
        }
    }
});

ChapStreamDirectives.directive('doneCommentEdit', function($http) {
    return {
        link: function(scope, element, attr) {
            element.bind('click', function(e, data) {
                $http.put('/api/comment-update/'+scope.comment.id, {body: scope.commentContent}).success(
                    function(data, status) {
                        scope.comment.body = scope.commentContent;
                        var comment = $(element).closest('.comment');
                        comment.find('.comment-edit-box').hide();
                        comment.find('.comment-content').show();
                    }
                );
            });
        }
    };
});

ChapStreamDirectives.directive('deleteComment', function($http) {
    return {
        link: function(scope, elem, element) {
            // TODO: Needs a confirm dialog.
            elem.bind('click', function(e, data) {
                $http.delete('/api/comment-delete/'+scope.comment.id).success(
                    function(data, status) {
                        // FIXME: comments.comments is not good practice
                        console.log(scope.post.comments.comments);
                        for (var i=0; i<scope.post.comments.comments.length; i++) {
                            if (scope.comment.id === scope.post.comments.comments[i].id) {
                                scope.post.comments.comments.splice(i, 1);
                                break;
                            }
                        }
                    }
                );
            });
        }
    }
});