function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}
$(document).ready(function () {
    $.get('api/v1.0/user/auth',function (resp) {
        if (resp.errno == '0'){
            $('#real-name').val(resp.data.real_name)
            $('#id-card').val(resp.data.id_card)
        }else {
            alert(resp.errmsg)
        }

    })
})

$('.btn-success').click(function (e) {
    //阻止表单的默认行为
    e.preventDefault();
    var real_name =$('#real-name').val();
    var  id_card=$('#id-card').val();
    var data={
        'real_name':real_name,
        'id_card':id_card
    }
    var jsondata=JSON.stringify(data)
    $.ajax({
        url:'api/v1.0/user/auth',
        type:'post',
        contentType:'application/json',
        dataType:'json',
        headers:{
            'X-CSRFToken':getCookie('csrf_token')
        },
        data:jsondata,

        success:function (resp) {
            if (resp.errno == '0'){
                window.location.reload()
            }else if(data.errno = '4001'){
                    location.href='/login.html';
                }
            else {
                alert(resp.errmsg)
            }
        }
    })
})
