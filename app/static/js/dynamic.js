$(document).ready(function () {
    //图片的显示
    $('.dynmaicimg').jqthumb({
            width: '100%',//宽度
            height: '250px',//高度
            zoom: '1',//缩放比例
            method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
     });
    //查看详情动态
    $('.detaillabel').click(function () {
        var dynamicid = $(this).parent().parent().parent().children('input[type=hidden]').val();
        window.location.href = "/dynamic/"+dynamicid;
    });

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
                    var newcomment='<li class="commentli" id="'+res['commentid']+'"><label>' +
                        '<a id="'+res['userid']+'" href="/user/'+res['userid']+'" class="answer">'+res['username']+'</a>：<span class="comment">&nbsp;'+res['content']+'</span></label>' +
                        '<span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                    li.append(newcomment);
                    input.val('');
                }else
                {
                    alertmsg=res['message'];
                    $('#alertmodel').modal('show');
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
                    var newcomment='<li class="commentli" id="'+res['commentid']+'"><label>' +
                        '<a id="'+res['userid']+'" href="/user/'+res['userid']+'" class="answer">'+res['username']+'</a>对&nbsp;<a>'+res['actorname']+'</a>：<span class="comment">'+res['content']+'</span></label>' +
                        '<span class="pull-right glyphicon glyphicon-remove hide remove"></span></li>';
                    li.append(newcomment);
                    $('.newcomment').remove();
                }else
                {
                    alertmsg=res['message'];
                    $('#alertmodel').modal('show');
                    $('.newcomment').remove();
                }
             }
         });
     });
     $('.commentlabel').click(function () {
        //获得焦点
        $(this).parent().parent().next().children('div').children('input')[0].focus();
     });
     $('.more').click(function(){
         var contentdiv=$(this).parent();
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
                 if(res['code']=='200')
                 {
                     contentdiv.text(res['content']);
                 }
             }
         });
     });
     var currentuserid=$('#username').children('input[type=hidden]').val();
     $('.commentpart').on('mouseover','.commentli',function(){
          var userid=$(this).children().children('a').attr('id');
          if(userid==currentuserid){
                $(this).children('.remove').removeClass('hide');
          }
     });
     $('.commentpart').on('mouseout','.commentli',function(){
          $(this).children('.remove').addClass('hide');
     });
     //
     $('.commentpart').on('click','.glyphicon-remove',function () {
          var li=$(this).parent();
          var commentid=li.attr('id');
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
                 if(res['code']=='200')
                 {
                     li.remove();
                 }
             }
         });
     });
     $('.likelabel').click(function(){
         var like=$(this);
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
                 if(res['code']=='200')
                 {
                     like.text('已点赞('+res['likecount']+')');
                 }
                 else if(res['code']=='201')//取消点赞之后返回201
                 {
                     like.text('点赞');
                 }else
                 {
                      alertmsg=res['message'];
                      $('#alertmodel').modal('show');
                      $('.newcomment').remove();
                 }
             }
         });
     });
});