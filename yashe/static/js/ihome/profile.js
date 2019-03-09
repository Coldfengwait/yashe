function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get('/api/v1.0/user/name',function (resp) {
        if (resp.errno == '0'){
            $('#user-name').val(resp.data.username)
        }else{
            alert(resp.errmsg);
        }

    },'json');
    $.get('/api/v1.0/user/avatar',function (resp) {
        if (resp.errno == '0'){
            $('#user-avatar').attr('src',resp.data.image_url)
        }else{
            alert(resp.errmsg);
        }

    },'json');
    $('#form-name').submit(function (e) {
        e.preventDefault();
        var user_name =$('#user-name').val()
        if (!user_name){
            alert('请填写用户名');
            return;
        }
        req_data={
            user_name:user_name
        };
        var jsondata =JSON.stringify(req_data)
        $.ajax({
            url:'/api/v1.0/user/name',
            type:'post',
            data:jsondata,
            contentType:'application/json',
            dataType:'json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            success:function (data) {
                if (data.errno =='0'){
                    window.location.reload()
                }else if(data.errno = '4001'){
                    location.href='/login.html';
                }
                else{
                    alert(data.errmsg)
                }

            }
        })

    })
    $('#form-avatar').submit(function (e) {
        //阻止表单的默认行为
        e.preventDefault();
        //利用jquery.form.min.js 提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url:'api/v1.0/user/avatar',
            type:'post',
            headers:{
                'x-CSRFtoken':getCookie('csrf_token')
            },
            dataType:'json',
            success:function (resp) {
                if (resp.errno == '0'){
                    //上传成功
                    var avatarUrl=resp.data.avatar_url;
                    $('#user-avatar').attr('src',avatarUrl);
                }else{
                    alert(resp.errmsg)
                }

            }
        })

    })
})