$(document).ready(function () {
    $('.commentbtn').click(function () {
         var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
         var input = $(this).parent().children('input');
         var content=input.val();
         var li = $(this).parent().prev();
         $.ajax({
             url: '/dynamic/comment',
             type: 'post',
             dataType: 'json',
             data: JSON.stringify({
                 id: dynamicid,
                 content: content,
                 type:'dynamic',
                 userid:'-1'
             }),
             headers: {
             "Content-Type": "application/json;charset=utf-8"
             },
             contentType: 'application/json; charset=utf-8',
             success: function (res) {
                if(res['code']=='200')
                {
                    var newcomment='<li id="'+res['commentid']+'"><label>' +
                        '<a id="'+res['userid']+'" href="/user/'+res['userid']+'" class="answer">'+res['username']+'</a>：<span class="comment">'+res['content']+'</span></label></li>';
                    li.append(newcomment);
                    input.val('');
                }
             }
         });
     });
    $('.commentpart').on('click','.comment',function () {
        if($('.newcomment').length>0) return ;
        var li=$(this).parent().parent();
        var name = $(this).parent().parent().children().children('.answer').text();
        var newcomment='<div class="newcomment"><textarea class="form-control" style="width:480px" placeholder="'+'回复'+name+'"></textarea>'+
            '<button type="button" class="btn btn-primary newcommentbtn">评论</button>' +
            '<button type="button" class="btn btn-danger closebtn">关闭</button><div/>';
        li.after(newcomment);
    });
    $('.commentpart').on('click','.closebtn',function () {
       $(this).parent().remove();
    });
     $('.commentpart').on('click','.newcommentbtn',function () {
         var input=$(this).prev();
         var content=input.val();
         var li=$(this).parent().prev();
         var commentid=li.attr('id');
         var userid=$(this).parent().prev().children().children('.answer').attr('id');
         $.ajax({
             url: '/dynamic/comment',
             type: 'post',
             dataType: 'json',
             data: JSON.stringify({
                 id: commentid,
                 content: content,
                 type:'comment',
                 userid:userid
             }),
             headers: {
             "Content-Type": "application/json;charset=utf-8"
             },
             contentType: 'application/json; charset=utf-8',
             success: function (res) {
                if(res['code']=='201')
                {
                    var newcomment='<li id="'+res['commentid']+'"><label>' +
                        '<a id="'+res['userid']+'" href="/user/'+res['userid']+'" class="answer">'+res['username']+'</a>对&nbsp;<a>'+res['actorname']+'</a>：<span class="comment">'+res['content']+'</span></label></li>';
                    li.append(newcomment);
                    $('.newcomment').remove();
                }
             }
         });
     });
});