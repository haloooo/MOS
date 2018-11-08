
console.log($("#demo select").val());

angular.module("AppChart", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            var detailscrollTop=0;
            $(window).mousewheel(function(event,delta) {  //鼠标监听事件，控制提示框上下滚动
                if (delta<0){   //往下滚
                    // if(detailscrollTop>700){  //防止计数太大,再往上滚的时候要多滚几次
                    //     detailscrollTop=700;
                    // }
                    detailscrollTop=detailscrollTop+100;
                    document.getElementById('mainText').scrollTop=detailscrollTop;
                }else{
                    // if(detailscrollTop< - 700){
                    //     detailscrollTop=-700;
                    // }
                    detailscrollTop=detailscrollTop-100;
                    document.getElementById('mainText').scrollTop=detailscrollTop;
                }
            });
            $rootScope.initDate = function () {
                var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
                $http.get(url_date).success(function(result) {
                    $("#from").val(result);
                    $("#to").val(result);
                });
            };
            $rootScope.initData = function () {
                $rootScope.objects = ["Total", "Assy", "Process"];
                $rootScope.selectedObject = "Total";
                $rootScope.types = [ 'Yield(Y1)', 'Yield(Y2)', 'Input', 'Output', 'NG'];
                $rootScope.selectedType = 'Yield(Y1)';
                var conts = ['Line', 'Assy', 'Process'];
                var html = [];
                for (var index in conts) {
                    var text = conts[index];
                    conts[index] = conts[index].replace(/\s/g, "&nbsp;");
                    html.push("<option value='"+ text +"'>" + conts[index] + "</option>");
                }
                $("#content").empty();
                $("#content").append(html.join(''));
            };
            $rootScope.search = function () {
                var from = $("#from").val();
                var to = $("#to").val();
                if(from == "" || to == "")
                {
                    toastr.info("Please choose the datetime first")
                    return
                }
                var arr = [],i=0;
                var chartType = '';
                var start = from;
                var end = to;
                var startTime = new Date(Date.parse(from));
                var endTime = new Date(Date.parse(to));
                if(startTime > endTime)
                {
                    toastr.info("Please choose correct datetime")
                }
                else
                {
                    var startTime = $rootScope.getDate(start);
                    var endTime = $rootScope.getDate(end);
                    var object = $rootScope.selectedObject;
                    var content = $("#content option:selected").val();
                    var type = $rootScope.selectedType;
                    var type_bak = $rootScope.selectedType;
                    if(type == "Yield(Y1)")
                    {
                        type = 'Y1'
                    }else if(type == 'Yield(Y2)')
                    {
                        type = 'Y2'
                    }
                    if(object == '対象' || content == '表示内容' || type == 'データの種類')
                    {
                        toastr.info("Please choose the search content");
                        return
                    }
                    while((endTime.getTime()-startTime.getTime())>=0){
                        var year = startTime.getFullYear();
                        var month = (startTime.getMonth()+1).toString().length==1?"0"+(startTime.getMonth()+1).toString():(startTime.getMonth()+1).toString();
                        var day = startTime.getDate().toString().length==1?"0"+startTime.getDate():startTime.getDate();
                        arr[i]=year+"-"+month+"-"+day;
                        startTime.setDate(startTime.getDate()+1);
                        i+=1;
                    }
                    var searchUrl = "search_chart?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to + "&object=" + object + "&content=" + content + "&type=" + type;
                    $("#search").attr("disabled",true);
                    $http.get(searchUrl).success(function(result)
                    {
                        $("#search").attr("disabled",false);
                        if(result == 101)
                        {
                            toastr.info('Connect to database failed');
                            return
                        }
                        else if(result == 102)
                        {
                            toastr.info('Operate database failed');
                            return
                        }
                        if(type == 'Y1' || type == 'Y2')
                        {
                            chartType = 'line';
                            if(type == 'Y1')
                            {
                                type_bak = "Yield(Y1)"
                            }
                            else
                            {
                                type_bak = "Yield(Y2)"
                            }
                            new Highcharts.Chart({
                                chart: {
                                    renderTo: 'showChart',
                                    type: chartType,
                                    zoomType: 'x'
                                },
                                title: {
                                    text: type_bak,
                                    x: -20 //center
                                },
                                credits: { enabled: false },
                                exporting: {
                                    enabled:false
                                },
                                subtitle: {
                                    text: '',
                                    x: -20
                                },
                                xAxis: {
                                    categories: arr
                                },
                                tooltip: {
                                    enabled: false,
                                },
                                plotOptions: {
                                    areaspline:{
                                        fillOpacity:0.5
                                    },
                                    series: {
                                        marker:{
                                          enabled:false
                                        },
                                        events: {
                                            mouseOut: function() {  //移出区域提示框消失
                                                $("#showDetail").hide();
                                            }
                                        },
                                        point:{
                                            events: {
                                                mouseOver: function(e) {  //移动到点上显示提示框
                                                    var num=e.target.series.index;
                                                    var index=e.target.index;
                                                    var sendhtml= "<div style=' font-weight: 600;height: 1px; float: left'>"+e.target.category+"</div><br><div id='mainText' style='overflow-y:scroll;height: 250px;'>";
                                                    for(var i = 0; i< e.target.series.chart.series.length;i++){
                                                        sendhtml+= "<div class='circle' style='background-color:"+e.target.series.chart.series[i].color+"; float: left '></div><div class='detailFont'>" + this.series.chart.series[i].name + ":<span class='numstyle'>" + this.series.chart.series[i].data[index].y +"%</span></div>";
                                                    }
                                                    sendhtml+="</div>";
                                                    $('#showDetail').css({"top": (e.target.plotY+30) + "px", "left": (e.target.plotX+100) + "px"});
                                                    $("#showDetail").show();
                                                    $("#showMain").html(sendhtml);
                                                    document.getElementById('mainText').scrollTop=detailscrollTop;
                                                }

                                            }
                                        }
                                    }
                                },
                                yAxis: {
                                    title: {
                                        text: ''
                                    },
                                    labels: {//y轴刻度文字标签
                                        formatter: function () {
                                            return this.value + '%';//y轴加上%
                                        },
                                        useHTML: true
                                    },
                                    plotLines: [{//区域划分线，0刻度
                                        value: 0,
                                        width: 1,
                                        color: '#3582d9'
                                    }]
                                },
                                legend: {
                                    layout: 'vertical',
                                    align: 'right',
                                    verticalAlign: 'top',
                                    x: -10,
                                    y: 0,
                                    borderWidth: 0
                                },
                                series: result
                            });
                        }
                        else
                        {
                            chartType = 'column';
                            // type_bak = type_bak + "(PCS)"
                            new Highcharts.Chart({
                                chart: {
                                    renderTo: 'showChart',
                                    type: chartType,
                                    zoomType: 'x'
                                },
                                title: {
                                    text: type_bak,
                                    x: -20 //center
                                },
                                credits: { enabled: false },
                                exporting: {
                                    enabled:false
                                },
                                subtitle: {
                                    text: '',
                                    x: -20
                                },
                                xAxis: {
                                    categories: arr
                                },
                                yAxis: {
                                    title: {
                                        text: ''
                                    },
                                    labels: {//y轴刻度文字标签
                                        formatter: function () {
                                            return this.value + 'PCS';//y轴加上%
                                        }
                                    },
                                    plotLines: [{//区域划分线，0刻度
                                        value: 0,
                                        width: 1,
                                        color: '#3582d9'
                                    }]
                                },
                                tooltip: {
                                    enabled: false,
                                },
                                plotOptions: {
                                    series: {
                                        events: {
                                            mouseOut: function() {  //移出区域提示框消失
                                                $("#showDetail").hide();
                                            }
                                        },
                                        point:{
                                            events: {
                                                mouseOver: function(e) {  //移动到点上显示提示框
                                                    var num=e.target.series.index;
                                                    var index=e.target.index;
                                                    var sendhtml= "<div style=' font-weight: 600;height: 1px; float: left'>"+e.target.category+"</div><br><div id='mainText' style='overflow-y:scroll;height: 250px;'>";
                                                    for(var i = 0; i< e.target.series.chart.series.length;i++){
                                                        sendhtml+= "<div class='circle' style='background-color:"+e.target.series.chart.series[i].color+"; float: left '></div><div class='detailFont'>" + this.series.chart.series[i].name + ":<span class='numstyle'>" + this.series.chart.series[i].data[index].y +"</span></div>";
                                                    }
                                                    sendhtml+="</div>";
                                                    $('#showDetail').css({"top": (e.target.plotY+30) + "px", "left": (e.target.plotX+115) + "px"});
                                                    $("#showDetail").show();
                                                    $("#showMain").html(sendhtml);
                                                    document.getElementById('mainText').scrollTop=detailscrollTop;
                                                }

                                            }
                                        }
                                    }
                                },
                                legend: {
                                    layout: 'vertical',
                                    align: 'right',
                                    verticalAlign: 'top',
                                    x: -10,
                                    y: 0,
                                    borderWidth: 0
                                },
                                series: result
                            });

                        }
                    });
                }
                detailscrollTop=0;//重新查询时滚动条复位
            };
            $rootScope.getDate = function(datestr){
                var temp = datestr.split("-");
                var date = new Date(temp[0],temp[1]-1,temp[2]);
                console.log(date);
                return date;
            };
            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
            $rootScope.initDate();
            $rootScope.initData();
            $rootScope.objectChanged = function() {
                var selectObject = $rootScope.selectedObject;
                if(selectObject == 'Total')
                {
                    var conts = ['Line','Assy','Process'];
                    var html = [];
                    for(var index in conts)
                    {
                        var text = conts[index];
                        conts[index] = conts[index].replace(/\s/g,"&nbsp;");
                        html.push("<option value='"+ text +"'>" + conts[index] + "</option>");
                    }
                    $("#content").empty();
                    $("#content").append(html.join(''));
                }
                else if(selectObject == 'Assy' || selectObject == 'Process')
                {
                    var url = "/get_select_content?model_name=" + $rootScope.model_name  +
                        "&object=" + selectObject;
                    $http.get(url).success(function(result)
                    {
                        if(result == 101)
                        {
                            toastr.info('Connect to database failed');
                            return
                        }
                        else if(result == 102)
                        {
                            toastr.info('Operate database failed');
                            return
                        }
                        var html = [];
                        for(var index in result)
                        {
                            var text = result[index];
                            result[index] = result[index].replace(/\s/g,"&nbsp;");
                            html.push("<option value='"+ text +"'>" + result[index] + "</option>");
                        }
                        $("#content").empty();
                        $("#content").append(html.join(''));
                    });
                }
            };
        });