'use strict';

/* Directives */

ChapStreamDirectives.directive('sendPost', function($http) {
    return {
        restrict: 'A',
        link: function (scope, elem, element) {
            elem.bind('click', function (e) {
                var receiver_groups = [];
                var receiver_users = [];
                var params = {'mystream': 0};
                $(".selectize-input").find(".item").each(function() {
                    var type = $(this).data("type");
                    var value = $(this).data("value");
                    if (typeof type === 'undefined' && value === 0) {
                        params['mystream'] = 1;
                    }
                    if (type === 'user') {
                        receiver_users.push(value);
                    }
                    if (type === 'group') {
                        receiver_groups.push(value);
                    }
                });
                if (receiver_groups.length != 0) {
                    params["receiver_groups"] = receiver_groups.join(",");
                }
                if (receiver_users.length != 0) {
                    params["receiver_users"] = receiver_users.join(",");
                }
                var url = '/api/timeline/post';
                if (params.length != 0) {
                    url += "?"+ $.param(params);
                }
                scope.inProgress = true;
                var form = $("#post-form");
                var post = form.val().trim();
                $http.post(url, {body: post}).success(
                    function(data, status) {
                        if (status === 200){
                            form.val('');
                            form.trigger('autosize.destroy');
                            form.trigger('focusout');
                            scope.$parent.restCharCount = 2000;
                            scope.restCharCount = 2000;
                            $("#chapstream-timeline form .receivers").css('display', 'none');
                            $('.post-form-control').css('display', 'none');
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
                $("#post-form").autosize({className: 'post-box', append: "\n"});
                scope.placeholder = $("#post-form").attr("placeholder");
                $("#post-form").attr("placeholder", "");
                $('.post-form-control').css('display', 'block');
                $("#chapstream-timeline form .receivers").css('display', 'block');
            });
            /*elem.bind('focusout', function(e) {
                console.log(e);
                if (scope.restCharCount === 2000) {
                    $('#post-form').trigger('autosize.destroy');
                    $("#post-form").attr('placeholder', scope.placeholder);
                    $('.post-form-control').css('display', 'none');
                    $("#chapstream-timeline form .receivers").css('display', 'none');
                }
            });*/
        }
    }
});

ChapStreamDirectives.directive('selectReceivers', function() {
    return {
        link: function(scope, elem, element) {
            var mystream = {
                'type': null,
                'identifier': '0',
                'name': 'My Stream'
            };
            var $select = $('#post-receivers').selectize({
                plugins: ['remove_button'],
                valueField: 'identifier',
                labelField: 'name',
                searchField: 'name',
                options: [mystream],
                create: false,
                render: {
                    option: function(item, escape) {
                        return '<div>' +
                            '<span class="user-name">' +
                                '<span class="name">'+escape(item.name)+'</span>' +
                            '</span>' +
                        '</div>';
                    }
                },
                load: function(query, callback) {
                    if (!query.length) return callback();
                    $.ajax({
                        url: 'http://127.0.0.1:8000/api/search/postreceivers/' + encodeURIComponent(query),
                        type: 'GET',
                        error: function() {
                            callback();
                        },
                        success: function(res) {
                            callback(res.items);
                        }
                    });
                },
                onInitialize: function() {
                    this.setValue(this.options[0]["identifier"])
                },
                onItemAdd: function(value, $item) {
                    var type = this.options[value]["type"];
                    $item.attr('data-type', type);
                },
            });
        }
    }
});

ChapStreamDirectives.directive('catchNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('new_post_event', function(e, data) {
                if (typeof(scope.user) != 'undefined' && scope.user.name != data.name) {
                    return;
                }
                if (scope.currentUser != data.name) {
                    scope.safeApply(function() {
                        if (typeof(scope.$parent.new_posts) === 'undefined') {
                            scope.$parent.new_posts = [data];
                        } else if (scope.$parent.new_posts.length === 0) {
                            scope.$parent.new_posts = [data];
                        } else {
                            scope.$parent.new_posts.unshift(data);
                        }
                    });
                    $("#new-post").slideDown(100);
                } else {
                    scope.safeApply(function() {
                        scope.$parent.posts.unshift(data);
                    });
                }
            });
        }
    }
});

ChapStreamDirectives.directive('releaseNewPosts', function($http) {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e, data) {
                scope.safeApply(function() {
                    for (var i=0; i<scope.new_post_count; i++) {
                        scope.posts.unshift(scope.new_posts[i]);
                    }
                    scope.$parent.$parent.new_posts = [];
                    $("#new-post").slideUp(100, function() {
                        scope.new_post_count = false;
                    });
                });
            });
        }
    }
})

ChapStreamDirectives.directive('countNewPost', function($http) {
    return {
        link: function(scope, elem, element) {
            scope.new_post_count = 0;
            elem.bind('new_post_event', function(e, data) {
                if (scope.currentUser != data.name) {
                    scope.safeApply(function() {
                        scope.new_post_count += 1;
                    });
                }
            });
        }
    }
});

ChapStreamDirectives.directive('postCancel', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('click', function(e) {
                $('#post-form').trigger('autosize.destroy');
                $("#post-form").attr('placeholder', scope.placeholder);
                $('.post-form-control').css('display', 'none');
                $("#chapstream-timeline form .receivers").css('display', 'none');
            });
        }
    }
});

ChapStreamDirectives.directive('postEvents', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            element.on('mouseenter', function() {
                $(element).find('.post-metadata .control').css('display', 'block');
            });
            element.on('mouseleave', function() {
                $(element).find('.post-metadata .control').css('display', 'none');
            });
        }
    }
});

ChapStreamDirectives.directive('autosizePostEdit', function() {
    return {
        link: function(scope, elem, element) {
            elem.bind('focusin', function(e) {
                elem.autosize();
            });
        }
    }
});

ChapStreamDirectives.directive('postEdit', function($http, $compile) {
    return {
        link: function(scope, element, attr) {
            element.bind('click', function(e, data) {
                var template = '<div class="post-edit-box"> \
                    <form role="form">\
                        <textarea id="post-edit-{{ post.post_id }}" class="post-form form-control" rows="1" count-char ng-model="commentContent" autosize-post-edit></textarea> \
                        <div class="post-edit-form-control"> \
                            <a class="post-edit-cancel pull-right" href="#" post-edit-cancel>Cancel</a> \
                            <button type="submit" class="post-edit-done pull-right btn btn-primary btn-xs" done-post-edit>Done</button> \
                            <span class="post-char-count pull-right">{{ restCharCount }}</span> \
                        </div> \
                    </form> \
                </div>';
                scope.safeApply(function() {
                    scope.commentContent = scope.post.body;
                    var post_edit_form = $(element).closest('.post').find(".post-edit-form");
                    $(element).closest('.post').find('.post-content').hide();
                    post_edit_form.html(template).show();
                    $compile(post_edit_form.contents())(scope);
                });
                $('#post-edit-'+scope.post.post_id).trigger('focusin');
            })
        }
    }
});


ChapStreamDirectives.directive('donePostEdit', function($http) {
    return {
        link: function(scope, element, attr) {
            element.bind('click', function(e, data) {
                var post_rid = scope.post.rid;
                var post_id = scope.post.post_id;
                $http.put('/api/timeline/post/'+post_rid+'/'+post_id, {body: scope.commentContent}).success(
                    function(data, status) {
                        scope.post.body = scope.commentContent;
                        var post = $(element).closest('.post');
                        post.find('.post-edit-box').hide();
                        post.find('.post-content').show();
                    }
                );
            });
        }
    };
});