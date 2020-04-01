var alertmsg;
$(document).ready(function(){
    $('.basebtn').click(function () {
        var id=$(this).attr('id');
        $.ajax({
            type: "POST",
            url: "/user/islogin",
            data: [],
            success: function (msg) {
                if(msg=='True'){
                    if (id=='uploadbtn')
                    {
                        $('#baseuploadermodel').modal('show');
                    }else
                    {
                        $('#basesuperresolutionmodel').modal('show');
                    }
                }else
                {
                    var curhref=window.location.pathname;
                    if(curhref=='/user/regloginpage')
                    {
                        return ;
                    }else
                    {
                        curhref=curhref.replace(/\//g,'%2F');
                        $(location).attr('href', '/user/regloginpage?next='+curhref);
                    }
                }
            }
        });
    });


    $('#basesuperresolutionmodel').on('shown.bs.modal', function() {
         $('#basesuperresolutionmodel-part').load('/image/superresolution',function(){
             var albumid;
             $('#basedropdown li').click(function () {
                     albumid=$(this).children().attr('id');
                     $.ajax({
                        type: "POST",
                        url: "/album/ajaxdetail",
                        data: JSON.stringify({
                            albumid:albumid
                        }),
                        success: function (msg) {
                            $('.baseimg').empty();
                            if(msg['imglist'].length==0)
                            {
                                var newdiv='<div>&nbsp;&nbsp;&nbsp;<label>没有需要处理的图片</label></div>';
                                $('.baseimg').append(newdiv);
                                return ;
                            }
                            var newidv='';
                            for (i = 0; i < msg['imglist'].length; i++) {
                               newidv+='<div class="col-sm-6 col-md-2"><a href="#" class="thumbnail">' +
                                   '<img id="'+msg['imglist'][i].id+'"src="'+msg['imglist'][i].url+'" class="img-responsive"/></a></div>';
                            }
                            newidv+='</div>';
                            $('.baseimg').append(newidv);
                        }
                     });
                 });
             var baseimgid;
             $(".baseimg").on('click', '.thumbnail', function () {
                  baseimgid=$(this).children('img').attr('id');
             });
             $('.basesuperbtn').click(function () {
                   if(typeof(baseimgid) == "undefined")
                   {
                        //$('#baseAlert').removeClass('hide').addClass('in');
                        //$('#baseAlert strong').text('请选择处理的图片');
                        alertmsg='请选择处理的图片';
                        $('#alertmodel').modal('show');
                        return ;
                   }
                    $.ajax({
                        url: '/image/superresolution',
                        type: 'post',
                        dataType: 'json',
                        data: JSON.stringify({
                            imgid:baseimgid,
                            albumid:albumid,
                            flag:true
                        }),
                        headers: {
                            "Content-Type": "application/json;charset=utf-8"
                        },
                        contentType: 'application/json; charset=utf-8',
                        beforeSend: function(){
                            $('.basesuperbtn').attr('disabled','disabled');
                        },
                        success: function (res) {
                            $('.basesuperbtn').removeAttr("disabled");
                            alertmsg=res['message'];
                            $('#alertmodel').modal('show');
                        }
                   });
             });
         });
     });
     $('#alertmodel').on('shown.bs.modal', function() {
          $('#alertmodel-part').load('/alert',{alertmsg:alertmsg});
     });
    $('#baseuploadermodel').on('shown.bs.modal', function() {
          $('#baseuploadermodel-part').load('/image/uploader',function(){
                $('#txt_file').fileinput({
                    language: 'zh', //设置语言
                    uploadUrl: '/image/uploader', //上传的地址
                    allowedFileExtensions: ['jpg', 'gif', 'png','bmp'],//接收的文件后缀
                    showUpload: true, //是否显示上传按钮
                    showCaption: false,//是否显示标题
                    browseClass: "btn btn-primary",
                    maxFileCount: 3, //表示允许同时上传的最大文件个数
                    enctype: 'multipart/form-data',
                    validateInitialCount:true,
                    previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
                    msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
                });
                $("#txt_file").on("fileuploaded", function (event,data) {
                     $('#model').modal('hide');
                     if(window.location.pathname=='/album/1'){
                         window.location.reload();
                     }
                 });
          });
    });

});