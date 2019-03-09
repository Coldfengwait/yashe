function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        //组织向后端传送的数据
        req_data={
            mobile:mobile,
            password:passwd
        };
        var jsondata =JSON.stringify(req_data)
        $.ajax({
            url:'/api/v1.0/sessions',
            type:'post',
            data:jsondata,
            contentType:'application/json',
            dataType:'json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            success:function (data) {
                if (data.errno =='0'){
                    location.href='/'
                }else{
                    $('#password-err span').html(data.errmsg);
                    $('#password-err').show()
                }

            }
        })
    });
})