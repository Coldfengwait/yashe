var cur_page = 1; // 当前页
var next_page = 1; // 下一页
var total_page = 1;  // 总页数
var house_data_querying = true;   // 是否正在向后台获取数据

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// 更新用户点选的筛选条件
function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}
//更新房源列表信息
//action表示从后端请求的数据在前段展示方式
//默认采用追加的方式
//action=renew 代表热面数据清空从新展示
function updateHouseData(action) {
    var areaId =$('.filter-area>li.active').attr('area-id')
    if (areaId == undefined) areaId = '';
    var startDate=$('#start-date').val();
    var endDate=$('#end-date').val();
    var sortKey=$('.filter-sort>li.active').attr('sort-key')
    var params={
        aid:areaId,
        sd:startDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };
    console.log('执行更新语句')
    $.get('/api/v1.0/houses',params,function (resp) {
        if(resp.errno =='0'){
            if (resp.data.total_page == 0){
                console.log('没有数据')
                $('.house-list').html('暂时没有符合您查询的房屋信息')

            }else {
                total_page=resp.data.total_page;
                if (action == 'renew'){
                    console.log('有数据')
                    cur_page=1;
                    $('.house-list').html(template('house-list-tmpl',{houses:resp.data.houses}))
                }else {
                    cur_page=next_page;
                    $('.houses-list').append(template('house-list-tmpl',{houses:resp.data.houses}))

                }
            }
        }

    })

}




$(document).ready(function(){
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate); 
    $("#end-date").val(endDate); 
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);

    //获取筛选条件中的城市区域信息
    $.get('api/v1.0/areas',function (resp) {
        if (resp.errno == '0'){
            //用户从首页跳转到这个搜索也ian时可能选择了城区，所有尝试从url中的查询字符串参数中提取出来
            var areaId=queryData['aid'];
            //如果提取到了城区id的数据
            if (areaId){
                //遍历从后端获取到的城区信息，添加到页面中
                for (var i=0;i<resp.data.length;i++){
                    //对于从url查询字符串参数中拿到的城区，在页面中做高亮展示
                    //后端获取到城区id是整形，从url参数中获取到的是字符串类型，
                    // 所以将url参数中获取到的转换为整型再进行对比
                    areaId=parseInt(areaId);
                    if (areaId == resp.data[i].aid){
                        $('.filter-area').append('<li area-id="'+ resp.data[i].aid+'" class="active">'+ resp.data[i].aname+'</li>');
                    }else{
                        $(".filter-area").append('<li area-id="'+ resp.data[i].aid+'">'+ resp.data[i].aname+'</li>');
                    }
                }
            }else {
                //如果url参数中每页城区信息，不需要做额外处理，直接遍历展示到页面中去
                for (var i=0;i<resp.data.length;i++){
                    $(".filter-area").append('<li area-id="'+ resp.data[i].aid+'">'+ resp.data[i].aname+'</li>');
                }
            }
            //在页面添加好城区选项信息后，更新展示房屋列表信息

            updateHouseData('renew');

             // 获取页面显示窗口的高度
            var windowHeight = $(window).height();
            window.onscroll=function(){
                // var a = document.documentElement.scrollTop==0? document.body.clientHeight : document.documentElement.clientHeight;
                var b = document.documentElement.scrollTop==0? document.body.scrollTop : document.documentElement.scrollTop;
                var c = document.documentElement.scrollTop==0? document.body.scrollHeight : document.documentElement.scrollHeight;
                // 如果滚动到接近窗口底部
                if(c-b<windowHeight+50){
                    // 如果没有正在向后端发送查询房屋列表信息的请求
                    if (!house_data_querying) {
                        // 将正在向后端查询房屋列表信息的标志设置为真，
                        house_data_querying = true;
                        // 如果当前页面数还没到达总页数
                        if(cur_page < total_page) {
                            // 将要查询的页数设置为当前页数加1
                            next_page = cur_page + 1;
                            // 向后端发送请求，查询下一页房屋数据
                            updateHouseData();
                        } else {
                            house_data_querying = false;
                        }
                    }
                }
            }
        }
    })



    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    //用户在选择筛选条件后，点击蒙区，刷新页面数据
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page=1;
        next_page=1;
        total_page=1;
        updateHouseData('renew');

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
})