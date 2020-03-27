$(document).ready(function () {
    $('#dynamicimg').fileinput({
                language: 'zh', //设置语言
                allowedFileExtensions: ['jpg', 'gif', 'png', 'bmp'],
                showCaption: false,
                showUpload: false,
                overwriteInitial: false,
                initialPreviewAsData: true,
                browseClass: "btn btn-success",
                maxFileCount: 3,
                enctype: 'multipart/form-data',
                validateInitialCount: true,
                msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
    });
    $('.dynmaicimg').jqthumb({
            width: '100%',//宽度
            height: '250px',//高度
            zoom: '1',//缩放比例
            method: 'auto'//提交方法，用于不同的浏览器环境，默认为‘auto’
     });
});
