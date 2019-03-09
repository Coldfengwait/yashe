$(document).ready(function(){
    $.get('/api/v1.0/house/auth',function (resp) {
        if (resp.errno != '0'){
            $('.auth-warn').show()
            $('#houses-list').hide()
        }else if (resp.errno == '4101'){
            location.href='/login.html'
        }
        else{
            $('.auth-warn').hide()
            $.get('/api/v1.0/house/info',function (resp) {
                if (resp.errno == '0'){
                    $('#houses-list').html(template('houses-list-tmp',{houses:resp.data.houses}))
                }else{
                    $('#houses-list').html(template('houses-list-tmp',{houses:[]}))
                }
            })
        }
    })
})