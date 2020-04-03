$(document).ready(function () {
    var offset = 3;
    var flag = true;
    $(document).scroll(function () {
        if($('.mod').length!=0&&typeof($("#r-1").attr("checked"))=='undefined') return ;
        if (flag == false) return;
        var scroH = $(document).scrollTop();  //滚动高度
        var viewH = $(window).height();  //可见高度
        var contentH = $(document).height();  //内容高度
        if (contentH - (scroH + viewH) <= 100) {  //距离底部高度小于100px
            var userid=$('#userid').val();
            flag = false;
            $.ajax({
                url: '/user/more',
                type: 'post',
                dataType: 'json',
                data: JSON.stringify({
                    offset: offset,
                    userid:userid
                }),
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                contentType: 'application/json; charset=utf-8',
                success: function (res) {
                    var newdynamic = '';
                    if (res['code'] == '200') {
                        for (i = 0; i < res['userlist'].length; i++) {
                            newdynamic += '<div class="panel panel-default">' +
                                '<input type="hidden" value="' + res['userlist'][i].id + '"><div class="panel-heading">' +
                                '<label class="time">' + res['userlist'][i].time + '</label></div>' +
                                '<div class="panel-body"><div>' + res['userlist'][i].content + ' &nbsp;&nbsp;';
                            //{% if dynamic['flag'] %}<label class="more"><a>全文</a></label>{% endif%}
                            if (res['userlist'][i].flag) {
                                newdynamic += '<label class="more"><a>全文</a></label>';
                            }
                            newdynamic += '</div><div class="row">';
                            for (j = 0; j < res['userlist'][i].imgs.length; j++) {
                                newdynamic += '<div class="col-sm-4 col-md-4"><div class="thumbnail"><img onload="drawImage(this)" src="' + res['userlist'][i].imgs[j] + '" class=" dynmaicimg"></div></div>'
                            }
                            newdynamic += '</div>';
                            newdynamic += '<div class="action">';
                            if (res['userlist'][i].likeflag) {
                                newdynamic += '<label class="likelabel">已点赞(' + res['userlist'][i].likecount + ')</label>&nbsp;&nbsp;';
                            } else {
                                newdynamic += '<label class="likelabel">点赞</label>&nbsp;&nbsp;&nbsp;';
                            }
                            newdynamic += '<label class="commentlabel">评论</label>&nbsp;&nbsp;&nbsp;';
                            if(typeof($("#r-1").attr("checked"))!='undefined'){
                                 newdynamic += '<label class="deletelabel">删除</label>';
                            }
                            //<label class="updatelabel">编辑</label>
                            newdynamic += '</div></div>';
                            newdynamic += '<div class="panel-footer commentpart"><ul class="list-unstyled">';
                            for (k = 0; k < res['userlist'][i].comments.length; k++) {
                                newdynamic += '<li id="' + res['userlist'][i].comments[k].id + '" class="commentli"><label >' +
                                    '<a id="' + res['userlist'][i].comments[k].userid + '" href="/user/' + res['userlist'][i].comments[k].userid + '" class="answer">' +
                                    '' + res['userlist'][i].comments[k].name + '</a>';
                                if (res['userlist'][i].comments[k].actorname != '-1') {
                                    newdynamic += '对<a>&nbsp;' + res['userlist'][i].comments[k].actorname + '</a> 回复';
                                }
                                newdynamic += '：<span class="comment">' + res['userlist'][i].comments[k].content + '</span></label><span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                            }
                            newdynamic += '</ul>';
                            newdynamic += '<div class="form-inline"><input type="text" class="form-control" style="width:780px" id="name" placeholder="写出你的想法"><button type="button" class="btn btn-primary commentbtn">评论</button></div>';
                            newdynamic += '</div></div>';
                        }
                        if($('.mod').length==0)
                        {
                            $('.tab').append(newdynamic);
                        }else {
                            $('.mod').append(newdynamic);
                        }
                    } else {
                        return ;
                    }
                    offset += 3;
                    flag = true;
                }
            });
        }
    });
});