$(document).ready(function(){
  var nickname=$('.username').text();
  var userid=$('#userid').val();
  var headurl=$('.userimg').attr('src');
  // 选项板的切换
  $(".tab-label").click(function(){
        var tab=$(this).attr('id');
        if(tab=='dynamictab')
        {
            $(location).attr('href', '/user/myspace');
        }else
        {
            $(location).attr('href', '/user/useralbum');
        }
  });
  // 显示编辑用户模态框
  $('.updateuserbtn').click(function(){
         $('#updateusermodel').modal('show');
    });
  // 显示模态框
  $('#updateusermodel').on('shown.bs.modal', function () {
         $('#updateusermodel-part').load('/user/updateuser', {userid:userid},function () {
              $('form').bootstrapValidator({
                  message: 'This value is not valid',
                　feedbackIcons: {
                    　　　　　　　　valid: 'glyphicon glyphicon-ok',
                    　　　　　　　　invalid: 'glyphicon glyphicon-remove',
                    　　　　　　　　validating: 'glyphicon glyphicon-refresh'
                　　　　　　　　   },
                fields: {
                    nickname: {
                        validators: {
                            notEmpty: {
                                message: '用户名不能为空'
                            }
                        }
                    },
                    signature: {
                        validators: {
                            notEmpty: {
                                message: '个人签名不能为空'
                            }
                        }
                    }
                }
            });
             $('#headurl').fileinput({
                language: 'zh', //设置语言
                allowedFileExtensions: ['jpg', 'gif', 'png', 'bmp'],
                showCaption: false,
                showUpload: false,
                overwriteInitial: true,
                initialPreview: [
                    headurl
                ],
                initialPreviewAsData: true,
                browseClass: "btn btn-success",
                maxFileCount: 1,
                enctype: 'multipart/form-data',
                validateInitialCount: true,
                msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
            });
         });
     });

  //
  $('.opensendmsgbtn').click(function(){
         $('#sendmsgmodel').modal('show');
  });
   $('#sendmsgmodel').on('shown.bs.modal', function () {
        $('#sendmsgmodel-part').load('/user/sendmessage', {nickname:nickname}, function () {
                $('.sendmsgbtn').click(function () {
                        var content=$('#messagecontent').val();
                        $.ajax({
                            url: '/user/sendmsg',
                            type: 'post',
                            dataType: 'json',
                            data: JSON.stringify({
                                userid:userid,
                                content:content
                            }),
                            headers: {
                                "Content-Type": "application/json;charset=utf-8"
                            },
                            contentType: 'application/json; charset=utf-8',
                            success: function (res) {
                                if(res['code']=='200')
                                {
                                    $('#sendmsgmodel').modal('hide');
                                }
                            }
                      });
                });
        });
     });
     $('.followuserdiv').on('click','.followuserbtn',function (){
         var userid=$(this).parent().parent().children('input[type=hidden]').val();
         $.ajax({
                    url: '/user/follow',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        userid:userid
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    success: function (res) {
                         $('.followuserdiv button').removeClass('followuserbtn').addClass('unfollowuserbtn');
                         $('.followuserdiv button').removeClass('btn-warning').addClass('btn-info');
                         $('.followuserdiv button').text('已关注');
                    }
           });
     });
     $('.followuserdiv').on('click','.unfollowuserbtn',function(){
         var userid=$(this).parent().parent().children('input[type=hidden]').val();
         $.ajax({
                    url: '/user/unfollow',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        userid:userid
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    success: function (res) {
                        $('.followuserdiv button').removeClass('unfollowuserbtn').addClass('followuserbtn');
                        $('.followuserdiv button').removeClass('btn-info').addClass('btn-warning');
                        $('.followuserdiv button').text('关注');
                    }
           });
    });
});