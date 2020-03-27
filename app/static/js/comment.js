$(document).ready(function () {
   $('.commentbtn').click(function(){
       var dynamicid=$(this).parent().parent().parent().parent().children('input[type=hidden]').val();
       var content=$(this).parent().children('input').val();
        $.ajax({
                url: '/dynamic/comment',
                type: 'post',
                dataType: 'json',
                data: JSON.stringify({
                    dynamicid:dynamicid,
                    content:content
                }),
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                contentType: 'application/json; charset=utf-8',
                success: function (res) {

                }
              });
   });
});