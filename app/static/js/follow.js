$(document).ready(function () {
    $('.noread').click(function () {
        var msgid=$(this).parent().children("input[type=hidden]").val();
        var btn=$(this);
        $.ajax({
                url: '/user/message/isread',
                type: 'post',
                dataType: 'json',
                data: JSON.stringify({
                    msgid:msgid
                }),
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                contentType: 'application/json; charset=utf-8',
                success: function (res) {
                    btn.attr('class','noread btn btn-danger disabled');
                    btn.text('已读');
                }
        });
    });
    var msgid;//全局表示模态框传入的值
    $('.look').click(function () {
        msgid=$(this).parent().parent().children("input[type=hidden]").val();
        $('#messagemodel').modal('show');
    });

    $('#messagemodel').on('shown.bs.modal', function() {
        $('#messagemodel-part').load('/user/messagedetail',{'msgid':msgid});
    });
});