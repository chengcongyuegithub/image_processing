$(document).ready(function(){
    $('#uploadbtn').click(function () {
        $.ajax({
            type: "POST",
            url: "/user/islogin",
            data: [],
            success: function (msg) {
                if(msg=='True'){
                    $('#model').modal('show')
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

    $('#model').on('shown.bs.modal', function() {
          $('#model-part').load('/image/uploader',function(){
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