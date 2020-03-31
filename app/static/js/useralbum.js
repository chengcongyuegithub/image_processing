$(document).ready(function () {
    var albumid;
    var albumcover;
    //编辑相册
    $('.updatebtn').click(function () {
        albumid = $(this).parent().parent().children('input[type=hidden]').val();
        albumcover = $(this).parent().parent().parent().children('img').attr('src');
        $(this).parent().parent().parent().parent().attr('id','choose');
        $('#albumupdatemodel').modal('show');
    });
    $('#albumupdatemodel').on('shown.bs.modal', function () {
        $('#albumupdatemodel-part').load('/album/updatealbum', {'albumid': albumid}, function () {
            $('form').bootstrapValidator({
            　 feedbackIcons: {
                　　　　　　　　valid: 'glyphicon glyphicon-ok',
                　　　　　　　　invalid: 'glyphicon glyphicon-remove',
                　　　　　　　　validating: 'glyphicon glyphicon-refresh'
            　　　　　　　　   },
                fields: {
                    name: {
                        validators: {
                            notEmpty: {
                                message: '相册名不能为空'
                            }
                        }
                    },
                    introduce: {
                        validators: {
                            notEmpty: {
                                message: '相册介绍不能为空'
                            }
                        }
                    }
                }
            });
            $('#updatefrontcover').fileinput({
                language: 'zh', //设置语言
                allowedFileExtensions: ['jpg', 'gif', 'png', 'bmp'],
                showCaption: false,
                showUpload: false,
                overwriteInitial: true,
                initialPreview: [
                    albumcover
                ],
                initialPreviewAsData: true,
                browseClass: "btn btn-success",
                maxFileCount: 1,
                enctype: 'multipart/form-data',
                validateInitialCount: true,
                msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
            });
            $('#deletebtn').click(function () {
                $.ajax({
                    url: '/album/delete',
                    type: 'post',
                    dataType: 'json',
                    data: JSON.stringify({
                        albumid:albumid
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=utf-8"
                    },
                    contentType: 'application/json; charset=utf-8',
                    success: function (res) {
                         $('#albumupdatemodel').modal('hide');
                         $('#choose').remove();
                    }
                  });
            });
        });
    });
    //相册的排版
    $('.row img').jqthumb({
        width: '100%',//宽度
        height: '142px',//高度
        //position : { y: '50%', x: '50%'},//从图片的中间开始产生缩略图
        zoom: '1',//缩放比例
        method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
    });
    //打开相册
    $('.openbtn').click(function () {
        var id = $(this).parent().parent().children('input[type=hidden]').val();
        $(location).attr('href', '/album/' + id);
    });
    //新建相册
    $('.addalbumbtn').click(function () {
        $('#albumaddmodel').modal('show');
    });
    $('#albumaddmodel').on('shown.bs.modal', function () {
        $('#albumaddmodel-part').load('/album/addalbum', {}, function () {
            $('form').bootstrapValidator({
                　feedbackIcons: {
                    　　　　　　　　valid: 'glyphicon glyphicon-ok',
                    　　　　　　　　invalid: 'glyphicon glyphicon-remove',
                    　　　　　　　　validating: 'glyphicon glyphicon-refresh'
                　　　　　　　　   },
                fields: {
                    name: {
                        validators: {
                            notEmpty: {
                                message: '相册名不能为空'
                            }
                        }
                    },
                    introduce: {
                        validators: {
                            notEmpty: {
                                message: '相册介绍不能为空'
                            }
                        }
                    }
                }
            });
            $('#addfrontcover').fileinput({
                language: 'zh', //设置语言
                allowedFileExtensions: ['jpg', 'gif', 'png', 'bmp'],
                showCaption: false,
                showUpload: false,
                overwriteInitial: true,
                initialPreviewAsData: true,
                browseClass: "btn btn-success",
                maxFileCount: 1,
                enctype: 'multipart/form-data',
                validateInitialCount: true,
                msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
            });
        });
    });
});