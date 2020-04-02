$(document).ready(function () {
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
                        return ;
                    }
                    offset += 5;
                    flag = true;
                }
            });
        }
    });
});