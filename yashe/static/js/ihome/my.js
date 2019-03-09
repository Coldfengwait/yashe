function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
    $.ajax({
        url:'/api/v1.0/session',
        type:'delete',
        headers:{
            'X-CSRFToken':getCookie('csrf_token')
        },
        dataType:'json',
        success:function (resp) {
            if(resp.errno == '0'){
                location.href='/index.html'
            }else if(data.errno = '4001'){
                    location.href='/login.html';
                }
            else {
            alert(resp.errmsg)
        }
        }
    })
}

$(document).ready(function(){
    $.get('/api/v1.0/user/info',function (resp) {
        if (resp.errno =='0'){
            $('#user-name').html(resp.data.username)
            $('#user-mobile').html(resp.data.mobile)
        }else if(data.errno = '4001'){
                    location.href='/login.html';
                }
        else {
            alert(resp.errmsg)
        }
    })
})