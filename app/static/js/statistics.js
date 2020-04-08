    var myChart = echarts.init(document.getElementById('main'));
    myChart.setOption({
        title: {
            text: '系统使用次数'
        },
        tooltip: {},
        legend: {
            data:['count']
        },
        xAxis: {
            data: []
        },
        yAxis: {},
        series: [{
            name: 'count',
            type: 'line',
            data: [] //初始化数据
        }]
    });
    var time = ["","","","","","","","","",""],
        count = [0,0,0,0,0,0,0,0,0,0];
    //准备好统一的 callback 函数
    var update_mychart = function (res) {
        myChart.hideLoading();
        time.push(res.data);
        count.push(res.count);
        if (time.length >= 10){
            time.shift();
            count.shift();
        }
        myChart.setOption({
            xAxis: {
                data: time
            },
            series: [{
                name: 'count', // 根据名字对应到相应的系列
                data: count
            }]
        });
    };
// 首次显示加载动画
    myChart.showLoading();

$(document).ready(function () {
    socket.on('count', function(data) {
          update_mychart(data);
    });
});