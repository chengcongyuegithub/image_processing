$(document).ready(function () {
    var imgid;
    var albumid=$('#albumid').val();
    $('.thumbnail').click(function(){
        imgid = $(this).children('input[type=hidden]').val();
        $(this).parent().attr('id','choose');
        $('#albumdetailmodel').modal('show');
     });
    $('.uploaderbtn').click(function(){
         $('#albumuploadmodel').modal('show');
    });
    $('#albumdetailmodel').on('shown.bs.modal', function (){
        $('#albumdetailmodel-part').load('/image/detail', {'imgid': imgid},function () {
             $('.deletebtn').click(function (){
                  var imgid=$(this).parent().children('input[type=hidden]').val();
                  $.ajax({
                    url: '/image/delete',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        imgid:imgid,
                        albumid:albumid
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    success: function (res) {
                         if(res['code']=='200'){
                            $('#albumdetailmodel').modal('hide');
                            $('#choose').remove();
                         }else
                         {
                             window.location.reload();
                         }
                    }
                  });
             });
             $('.superresolutionbtn').click(function (){
                  var imgid=$(this).parent().children('input[type=hidden]').val();
                  $.ajax({
                    url: '/image/superresolution',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        imgid:imgid,
                        albumid:albumid
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    beforeSend: function(){
                        $('.superresolutionbtn').attr('disabled','disabled');
    	            },
                    success: function (res) {
                        $('.superresolutionbtn').removeAttr("disabled");
                        if(res['code']=='200')//处理成功
                        {
                             window.location.reload();
                        }
                        else
                        {
                            if(res['code']=='201')//禁用
                            {
                                $('.superresolutionbtn').attr('disabled','disabled');
                            }
                            $('.alert-danger').removeClass('hide').addClass('in');
                            $('.alert-danger strong').text(res['message']);
                        }
                    }
                  });
             });
             var flag=true;
             $('.comparebtn').click(function (){
                  var imgid=$(this).parent().children('input[type=hidden]').val();
                  $.ajax({
                    url: '/image/compare',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        imgid:imgid,
                        flag:flag
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    success: function (res) {
                        if(flag){
                            $('.col-md-6').removeClass('col-md-offset-3');
                            var newdiv='<div class="col-md-6"><img src="'+res['orginurl']+'" class="img-responsive"/></div>';
                            $('.col-md-6').parent().append(newdiv);
                            flag=false;
                        }
                    }
                  });
             });
        });
    });
    $('.row img').jqthumb({
            width: '100%',//宽度
            height: '250px',//高度
            zoom: '1',//缩放比例
            method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
     });
    $('#albumupload').fileinput({
                    language: 'zh', //设置语言
                    uploadUrl: '/image/uploader',
                    allowedFileExtensions: ['jpg', 'gif', 'png','bmp'],
                    showCaption: false,
                    browseClass: "btn btn-primary",
                    maxFileCount: 1,
                    uploadExtraData:{albumid:albumid},
                    enctype: 'multipart/form-data',
                    validateInitialCount:true,
                    previewFileIcon: "<i class='glyphicon glyphicon-king'></i>"
                });
    $("#albumupload").on("fileuploaded", function () {
        window.location.reload();
    });
});