function drawImage(img) {
    $(img).jqthumb({
        width: '100%',//宽度
        height: '250px',//高度
        zoom: '1',//缩放比例
        method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
    });
}
$(document).ready(function () {
    //图片的显示
    $('.dynmaicimg').jqthumb({
        width: '100%',//宽度
        height: '250px',//高度
        zoom: '1',//缩放比例
        method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
    });
    //查看详情动态
    $('.main').on('click', '.detaillabel', function () {
        var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
        window.open("/dynamic/" + dynamicid);
    });
//.commentbtn
    $('.main').on('click', '.commentbtn', function () {
        var input = $(this).parent().children('input');
        var content = input.val();
        if (content == '') {
            alertmsg = '评论不能为空';
            $('#alertmodel').modal('show');
            return;
        }
        var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
        var li = $(this).parent().prev();
        $.ajax({
            url: '/dynamic/comment',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                id: dynamicid,
                content: content,
                type: 'dynamic',
                userid: '-1'
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '200') {
                    var newcomment = '<li class="commentli" id="' + res['commentid'] + '"><label>' +
                        '<a id="' + res['userid'] + '" href="/user/' + res['userid'] + '" class="answer">' + res['username'] + '</a>：<span class="comment">&nbsp;' + res['content'] + '</span></label>' +
                        '<span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                    li.append(newcomment);
                    input.val('');
                } else {
                    alertmsg = res['message'];
                    $('#alertmodel').modal('show');
                }
            }
        });
    });
    $('.main').on('click', '.comment', function () {
        if ($('.newcomment').length > 0) return;
        var li = $(this).parent().parent();
        var name = $(this).parent().parent().children().children('.answer').text();
        var newcomment = '<div class="newcomment"><textarea class="form-control" style="width:480px" placeholder="' + '回复' + name + '"></textarea>' +
            '<button type="button" class="btn btn-primary newcommentbtn">评论</button>' +
            '<button type="button" class="btn btn-danger closebtn">关闭</button><div/>';
        li.after(newcomment);
    });
    $('.main').on('click', '.closebtn', function () {
        $(this).parent().remove();
    });
    $('.main').on('click', '.newcommentbtn', function () {
        var input = $(this).prev();
        var content = input.val();
        var li = $(this).parent().prev();
        var commentid = li.attr('id');
        var userid = $(this).parent().prev().children().children('.answer').attr('id');
        $.ajax({
            url: '/dynamic/comment',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                id: commentid,
                content: content,
                type: 'comment',
                userid: userid
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '201') {
                    var newcomment = '<li class="commentli" id="' + res['commentid'] + '"><label>' +
                        '<a id="' + res['userid'] + '" href="/user/' + res['userid'] + '" class="answer">' + res['username'] + '</a>对&nbsp;<a>' + res['actorname'] + '</a>：<span class="comment">' + res['content'] + '</span></label>' +
                        '<span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                    li.append(newcomment);
                    $('.newcomment').remove();
                } else {
                    alertmsg = res['message'];
                    $('#alertmodel').modal('show');
                    $('.newcomment').remove();
                }
            }
        });
    });
    $('.main').on('click', '.commentlabel', function () {
        //获得焦点
        $(this).parent().parent().next().children('div').children('input')[0].focus();
    });
    $('.main').on('click', '.more', function () {
        var contentdiv = $(this).parent();
        var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
        $.ajax({
            url: '/dynamic/more',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                id: dynamicid
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '200') {
                    contentdiv.text(res['content']);
                    var newbtn = '&nbsp;&nbsp;<label class="packup"><a>收起</a></label>';
                    contentdiv.append(newbtn);
                }
            }
        });
    });
    $('.main').on('click', '.packup', function () {
        var contentdiv = $(this).parent();
        var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
        $.ajax({
            url: '/dynamic/packup',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                id: dynamicid
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '200') {
                    contentdiv.text(res['content']);
                    var newbtn = '&nbsp;&nbsp;<label class="more"><a>全文</a></label>';
                    contentdiv.append(newbtn);
                }
            }
        });
    });

    var currentuserid = $('#username').children('input[type=hidden]').val();
    $('.main').on('mouseover', '.commentli', function () {
        var userid = $(this).children().children('a').attr('id');
        if (userid == currentuserid) {
            $(this).children('.remove').removeClass('hide');
        }
    });
    $('.main').on('mouseout', '.commentli', function () {
        $(this).children('.remove').addClass('hide');
    });
    //
    $('.main').on('click', '.glyphicon-remove', function () {
        var li = $(this).parent();
        var commentid = li.attr('id');
        $.ajax({
            url: '/dynamic/deletecomment',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                commentid: commentid
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '200') {
                    li.remove();
                }
            }
        });
    });
    $('.main').on('click','.likelabel',function () {
        var like = $(this);
        var dynamicid = like.parent().parent().parent().children('input[type=hidden]').val();
        //alert(dynamicid);
        $.ajax({
            url: '/dynamic/like',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                dynamicid: dynamicid
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                //点赞之后返回200
                if (res['code'] == '200') {
                    like.text('已点赞(' + res['likecount'] + ')');
                }
                else if (res['code'] == '201')//取消点赞之后返回201
                {
                    like.text('点赞');
                } else {
                    alertmsg = res['message'];
                    $('#alertmodel').modal('show');
                    $('.newcomment').remove();
                }
            }
        });
    });
    var offset = 5;
    var flag = true;
    $(document).scroll(function () {
        if (flag == false) return;
        var scroH = $(document).scrollTop();  //滚动高度
        var viewH = $(window).height();  //可见高度
        var contentH = $(document).height();  //内容高度
        if (contentH - (scroH + viewH) <= 100) {  //距离底部高度小于100px
            flag = false;
            $.ajax({
                url: '/more',
                type: 'post',
                dataType: 'json',
                data: JSON.stringify({
                    offset: offset
                }),
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                contentType: 'application/json; charset=utf-8',
                success: function (res) {
                    var newdynamic = '';
                    if (res['code'] == '200') {
                        for (i = 0; i < res['indexlist'].length; i++) {
                            newdynamic += '<div class="panel panel-default">' +
                                '<input type="hidden" value="' + res['indexlist'][i].id + '"><div class="panel-heading">' +
                                '<a href="/user/' + res['indexlist'][i].userid + '">' +
                                '<img src="' + res['indexlist'][i].headurl + '" class="img-circle head"/></a>' +
                                '<label>' + res['indexlist'][i].name + '</label><label class="pull-right time">' + res['indexlist'][i].time + '</label></div>' +
                                '<div class="panel-body"><div>' + res['indexlist'][i].content + ' &nbsp;&nbsp;';
                            //{% if dynamic['flag'] %}<label class="more"><a>全文</a></label>{% endif%}
                            if (res['indexlist'][i].flag) {
                                newdynamic += '<label class="more"><a>全文</a></label>';
                            }
                            newdynamic += '</div><div class="row">';
                            for (j = 0; j < res['indexlist'][i].imgs.length; j++) {
                                newdynamic += '<div class="col-sm-4 col-md-4"><div class="thumbnail"><img onload="drawImage(this)" src="' + res['indexlist'][i].imgs[j] + '" class=" dynmaicimg"></div></div>'
                            }
                            newdynamic += '</div>';
                            newdynamic += '<div class="action">';
                            if (res['indexlist'][i].likeflag) {
                                newdynamic += '<label class="likelabel">已点赞(' + res['indexlist'][i].likecount + ')</label>&nbsp;&nbsp;';
                            } else {
                                newdynamic += '<label class="likelabel">点赞</label>&nbsp;&nbsp;&nbsp;';
                            }
                            newdynamic += '<label class="commentlabel">评论</label>&nbsp;&nbsp;&nbsp;<label class="detaillabel">详情</label>';
                            newdynamic += '</div></div>';
                            newdynamic += '<div class="panel-footer commentpart"><ul class="list-unstyled">';
                            for (k = 0; k < res['indexlist'][i].comments.length; k++) {
                                newdynamic += '<li id="' + res['indexlist'][i].comments[k].id + '" class="commentli"><label >' +
                                    '<a id="' + res['indexlist'][i].comments[k].userid + '" href="/user/' + res['indexlist'][i].comments[k].userid + '" class="answer">' +
                                    '' + res['indexlist'][i].comments[k].name + '</a>';
                                if (res['indexlist'][i].comments[k].actorname != '-1') {
                                    newdynamic += '对<a>&nbsp;' + res['indexlist'][i].comments[k].actorname + '</a> 回复';
                                }
                                newdynamic += '：<span class="comment">' + res['indexlist'][i].comments[k].content + '</span></label><span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                            }
                            newdynamic += '</ul>';
                            newdynamic += '<div class="form-inline"><input type="text" class="form-control" style="width:780px" id="name" placeholder="写出你的想法"><button type="button" class="btn btn-primary commentbtn">评论</button></div>';
                            newdynamic += '</div></div>';
                        }
                        $('.main').append(newdynamic);
                    } else {

                    }
                    offset += 5;
                    flag = true;
                }
            });
        }
    });
});