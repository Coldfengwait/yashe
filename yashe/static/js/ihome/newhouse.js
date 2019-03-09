function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    //获取城区信息
    $.get('/api/v1.0/areas',function (resp) {
        if (resp.errno == '0'){
            var areas =resp.data;
            // for (i=0;i<areas.length;i++){
            //     var area =areas[i]
            //     $('#area-id').append('<option value="'+area.aid+'">'+area.aname+'</option>')
            // }
            //使用js模板
            var html=template("areas-tmp",{areas:areas})
            $('#area-id').html(html);

        }else{
            alert(resp.errmsg)
        }
    },'json')
    $('#form-house-info').submit(function (e) {
        e.preventDefault()
        //处理表单数据
        var data={};
        $('#form-house-info').serializeArray().map(function(x){data[x.name]=x.value})
        //收集房屋设施的id信息
        var facility=[]
        $(':checked[name=facility]').each(function(index,x){facility[index]=$(x).val()})
        data.facility=facility;
        $.ajax({
            url:'/api/v1.0/houses/info',
            type:'post',
            contentType:'application/json',
            data:JSON.stringify(data),
            dataType:'json',
            headers:{
                'X-CSRFTOKEN':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno == '4101'){
                    location.href='/login.html'
                }else if (resp.errno == '0'){
                    $('#form-house-info').hide()
                    $('#form-house-image').show()
                    //设置图片变淡中的house_id
                    $('#house-id').val(resp.data.house_id);
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });
    $('#form-house-image').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/api/v1.0/houses/image',
            type:'post',
            dataType:'json',
            headers:{
                'X-CSRFTOKEN':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno == '4101'){
                    location.href='/login.html'
                }else if (resp.errno == '0'){
                    $('.house-image-cons').append('<img src="'+resp.data.image_url+ '">');
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })
})