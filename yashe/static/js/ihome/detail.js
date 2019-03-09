function hrefBack() {
    history.go(-1);
}
// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    //获取详情页面需要展示的房屋编号
    var queryData =decodeQuery();
    var houseId =queryData['id']
    //获取该房屋的详细信息
    $.get('/api/v1.0/houses/'+houseId,function (resp) {
        if (resp.errno == '0'){
            //使用框架渲染前端
            $('.swiper-container').html(template('houses-list-tmpl',{img_urls:resp.data.house.img_urls,price:resp.data.house.price}))
            $('.detail-con').html(template('houses-detail-tmpl',{house:resp.data.house}))
            if (resp.data.user_id != resp.data.house.user_id){
                console.log(resp.data.user_id)
                console.log(resp.data.house.user_id)
                $('.book-house').attr('href','/booking.html?hid='+resp.data.house.hid);
                $('.book-house').show()
            }
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            })
        }
    })

})