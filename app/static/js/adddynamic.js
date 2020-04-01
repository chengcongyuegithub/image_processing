$(document).ready(function () {
    var imgurl=$('#img').val();
    var compareurl=$('#compareimg').val();
    //添加
    $('#dynamicimg').fileinput({
                language: 'zh', //设置语言
                allowedFileExtensions: ['jpg', 'gif', 'png', 'bmp'],
                showCaption: false,
                showUpload: false,
                overwriteInitial: false,
                initialPreview: [
                    imgurl,compareurl
                ],
                initialPreviewAsData: true,
                browseClass: "btn btn-success",
                maxFileCount: 3,
                enctype: 'multipart/form-data',
                validateInitialCount: true,
                msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
    });
    //添加
    $('form').bootstrapValidator({
        　feedbackIcons: {
            　　　　　　　　valid: 'glyphicon glyphicon-ok',
            　　　　　　　　invalid: 'glyphicon glyphicon-remove',
            　　　　　　　　validating: 'glyphicon glyphicon-refresh'
        　　　　　　　　   },
        fields: {
            dynamiccontent: {
                validators: {
                    notEmpty: {
                        message: '内容不能为空'
                    }
                }
            }
        }
    });
});
