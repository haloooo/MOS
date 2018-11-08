angular.module("AppTrendChart", [])
    .run(
        function($rootScope, $http, $interval, $location,$timeout) {
            var detailscrollTop=0;
            $('#showChart').mousewheel(function(event,delta) {  //鼠标监听事件，控制提示框上下滚动
                if (delta<0){   //往下滚
                    // if(detailscrollTop>1000){  //防止计数太大,再往上滚的时候要多滚几次
                    //     detailscrollTop=1000;
                    // }
                    detailscrollTop=detailscrollTop+100;
                    document.getElementById('mainText').scrollTop=detailscrollTop;
                }else{
                    // if(detailscrollTop< - 1000){
                    //     detailscrollTop=-1000;
                    // }
                    detailscrollTop=detailscrollTop-100;
                    document.getElementById('mainText').scrollTop=detailscrollTop;
                }
            });
            $rootScope.initDataType = function () {
                var result = ['NG rate','NG'];
                $rootScope.dataTypes = result;
                $rootScope.selectedDataType = result[0];
            };
            // get Time Part
            $rootScope.get_tps = function() {
                var url = "/get_tps?model_name=" + $rootScope.model_name  +"&line=" + "&assy=";
                $http.get(url).success(function(result) {
                    if (result === 101) {
                        toastr.info('Connect to database failed');
                        return;
                    }
                    else if (result === 102) {
                        toastr.info('Operate database failed');
                        return;
                    }
                    $rootScope.tps = result;
                    $rootScope.selectedTp = result[0].time_part;
                    $rootScope.mulSelect();
                });
            };
            $rootScope.mulSelect = function () {
                $timeout(function () {
                    $('#example-getting-started').multiselect({
                        maxHeight:'34px',
                        buttonWidth:'120px',
                        nonSelectedText: 'None Select'

                    });
                });
            };
            $rootScope.doSearch = function () {
                $rootScope.checklist = [];
                var from = $("#from").val();
                var to = $("#to").val();
                if(from == "" || to == "")
                {
                    toastr.info("Please choose the datetime first");
                    return
                }
                var startTime = new Date(Date.parse(from));
                var endTime = new Date(Date.parse(to));
                if(startTime > endTime)
                {
                    toastr.info("Please choose correct datetime");
                    return
                }
                var process = $rootScope.selectedProcess;
                var inspect = $('#inspect').val();
                if(inspect.length == 0){
                    toastr.info("Please fill in the Inspect value");
                    return
                }
                var datatype = $rootScope.selectedDataType;
                if(datatype == 'NG rate'){
                    datatype = 'Y2'
                }
                var tpindex = $("#example-getting-started").val();
                if(tpindex.length == 0){
                    toastr.info("Please choose TimePart");
                    return
                }
                for(var i=0;i<tpindex.length;i++)
                {
                    $rootScope.checklist.push($rootScope.tps[tpindex[i]].time_part);
                }
                var arr_ = {
                    'model':$rootScope.model_name,
                    'from':from,
                    'to':to,
                    'process':process,
                    'inspect':inspect,
                    'datatype':datatype,
                    'timepart':$rootScope.checklist
                };
                var arr = [],i=0;
                var startTime = $rootScope.getDate(from);
                var endTime = $rootScope.getDate(to);
                while((endTime.getTime()-startTime.getTime())>=0){
                    var year = startTime.getFullYear();
                    var month = (startTime.getMonth()+1).toString().length==1?"0"+(startTime.getMonth()+1).toString():(startTime.getMonth()+1).toString();
                    var day = startTime.getDate().toString().length==1?"0"+startTime.getDate():startTime.getDate();
                    if(month.length > 1)
                    {
                        if(month.substr(0, 1) == '0')
                        {
                            month = month.substr(1,month.length);
                        }
                    }
                    if(day.length > 1)
                    {
                        if(day.substr(0, 1) == '0')
                        {
                            day = day.substr(1,day.length);
                        }
                    }
                    arr[i]=month+"/"+day;
                    startTime.setDate(startTime.getDate()+1);
                    i+=1;
                }
                $("#search").attr('disabled',true);
                $.ajax({
                    url: 'search_trend',
                    traditional:true,
                    async:true,
                    type:'POST',
                    data:{
                        'model':$rootScope.model_name,
                        'from':from,
                        'to':to,
                        'process':process,
                        'inspect':inspect,
                        'datatype':datatype,
                        'timepart':$rootScope.checklist
                    },
                    success:function (result) {
                        if(result == 101)
                        {
                            toastr.info('Connect to database failed');
                            $("#exportFile").attr('disabled',true);
                            return
                        }
                        else if(result == 102)
                        {
                            toastr.info('Operate database failed');
                            $("#exportFile").attr('disabled',true);
                            return
                        }
                        if(result.length == 0)
                        {
                            toastr.info('Can not find any record!');
                            $("#search").attr("disabled",false);
                            $("#exportFile").attr('disabled',true);
                            return
                        }
                        for(var i = 0,l = result.length;i<l;i++)
                        {
                            for(var key in result[i])
                            {
                                if(key == 'status')
                                {
                                    $("#target").hide();
                                    toastr.info('query error in server!');
                                    $("#exportFile").attr('disabled',true);
                                    $("#search").attr("disabled",false);
                                    return;
                                }
                            }
                        }
                        //chart
                        if($rootScope.selectedDataType == 'NG rate'){
                            new Highcharts.Chart({
                                chart: {
                                    renderTo: 'showChart',
                                    type: 'line',
                                    zoomType: 'x'
                                },
                                title: {
                                    text: $rootScope.selectedDataType,
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
                                            return this.value + '%';//y轴加上%
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
                                    areaspline:{
                                        fillOpacity:0.5
                                    },
                                    series: {
                                        marker:{
                                          enabled:false
                                        },
                                        events: {
                                            // click: function(e) {   //点击其他线颜色变化
                                            //     var num=e.point.series.index;
                                            //     var index=e.point.index;
                                            //     for(var i = 0; i< this.chart.series.length;i++){
                                            //         this.chart.series[i].update({
                                            //             color: '#D4D4D4'
                                            //         });
                                            //     }
                                            //     this.chart.series[num].update({
                                            //         color: '#E066FF'
                                            //     });
                                            //     $("#showDetail").hide();
                                            //
                                            // },
                                            mouseOut: function() {  //移出区域提示框消失
                                                $("#showDetail").hide();
                                                // document.documentElement.style.overflowY = 'scroll';
                                                jQuery("html").getNiceScroll().show();
                                            }
                                        },
                                        point:{
                                            events: {
                                                mouseOver: function(e) {  //移动到点上显示提示框
                                                    var num=e.target.series.index;
                                                    var index=e.target.index;
                                                    var sendhtml= "<div style=' font-weight: 600;height: 1px; float: left;z-index:99999'>"+e.target.category+"</div><br><div id='mainText' style='overflow-y:scroll;height: 250px;'>";
                                                    for(var i = 0; i< e.target.series.chart.series.length;i++){
                                                        sendhtml+= "<div class='circle' style='background-color:"+e.target.series.chart.series[i].color+"; float: left '></div><div class='detailFont'>" + this.series.chart.series[i].name + ":<span class='numstyle'>" + this.series.chart.series[i].data[index].y +"%</span></div>";
                                                    }
                                                    sendhtml+="</div>";
                                                    $('#showDetail').css({"top": (e.target.plotY) + "px", "left": (e.target.plotX+200) + "px"});
                                                    $("#showDetail").show();
                                                    // document.documentElement.style.overflowY = 'hidden';
                                                     jQuery("html").getNiceScroll().hide();
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
                                series: $.parseJSON( result)
                            });
                        }else{
                            new Highcharts.Chart({
                                chart: {
                                    renderTo: 'showChart',
                                    type: 'line',
                                    zoomType: 'x'
                                },
                                title: {
                                    text: $rootScope.selectedDataType,
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
                                    areaspline:{
                                        fillOpacity:0.5
                                    },
                                    series: {
                                        marker:{
                                          enabled:false
                                        },
                                        events: {
                                            // click: function(e) {   //点击其他线颜色变化
                                            //     var num=e.point.series.index;
                                            //     var index=e.point.index;
                                            //     for(var i = 0; i< this.chart.series.length;i++){
                                            //         this.chart.series[i].update({
                                            //             color: '#D4D4D4'
                                            //         });
                                            //     }
                                            //     this.chart.series[num].update({
                                            //         color: '#E066FF'
                                            //     });
                                            //     $("#showDetail").hide();
                                            //
                                            // },
                                            mouseOut: function() {  //移出区域提示框消失
                                                $("#showDetail").hide();
                                                // document.documentElement.style.overflowY = 'scroll';
                                                jQuery("html").getNiceScroll().show();
                                            }

                                        },
                                        point:{
                                            events: {
                                                mouseOver: function(e) {  //移动到点上显示提示框
                                                    var num=e.target.series.index;
                                                    var index=e.target.index;
                                                    var sendhtml= "<div style=' font-weight: 600;height: 1px; float: left;z-index:99999'>"+e.target.category+"</div><br><div id='mainText' style='overflow-y:scroll;height: 250px;'>";
                                                    for(var i = 0; i< e.target.series.chart.series.length;i++){
                                                        sendhtml+= "<div class='circle' style='background-color:"+e.target.series.chart.series[i].color+"; float: left '></div><div class='detailFont'>" + this.series.chart.series[i].name + ":<span class='numstyle'>" + this.series.chart.series[i].data[index].y +"</span></div>";
                                                    }
                                                    sendhtml+="</div>";
                                                    $('#showDetail').css({"top": (e.target.plotY) + "px", "left": (e.target.plotX+200) + "px"});
                                                    $("#showDetail").show();
                                                    // document.documentElement.style.overflowY = 'hidden';
                                                     jQuery("html").getNiceScroll().hide();
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
                                series: $.parseJSON( result)
                            });
                        }
                        var jsonData = $.parseJSON( result);
                        for(var i = 0; i < jsonData.length; i++){
                            for(var j = 0; j < jsonData[i].data_tb.length; j++){
                                if(jsonData[i].data_tb[j] == 'NP'){
                                    jsonData[i].data_tb[j] = 0;
                                }
                                if(jsonData[i].data_tb[j] == '0.00%'){
                                    jsonData[i].data_tb[j] = 0;
                                }
                            }
                        }
                        //table
                        $rootScope.datelist = arr;
                        $rootScope.datalist = jsonData;
                        $rootScope.$apply();
                        $('#process').show();
                        $("#search").attr('disabled',false);
                        $("#exportFile").attr('disabled',false);
                    }
                });
            };
            $rootScope.getDate = function(datestr){
                var temp = datestr.split("-");
                var date = new Date(temp[0],temp[1]-1,temp[2]);
                console.log(date);
                return date;
            };
            $rootScope.getTrendData = function () {
                var url = "get_Trend_Data?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result)
                {
                    $rootScope.trendData = result;
                });
            };
            $rootScope.get_process = function(){
                var url = "/get_select_content?model_name=" + $rootScope.model_name  +
                    "&object=Process";
                $http.get(url).success(function(result){
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
                    $rootScope.process = result;
                    $rootScope.selectedProcess = result[0];
                    // $rootScope.get_inspect();
                });
            };
            $rootScope.get_inspect = function(){
                var from = $("#from").val();
                var to = $("#to").val();
                var process = $rootScope.selectedProcess;
                var url = "/getInspect?model_name=" + $rootScope.model_name  +
                    "&from=" + from + "&to=" + to + "&process=" + process;
                $http.get(url).success(function(result){
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
                    $rootScope.inspect = result;
                    $rootScope.selectedInspect = result[0];
                });
            };
            $rootScope.initSearchDate = function(){
                var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
                $http.get(url_date).success(function(result) {
                    $rootScope.from = result;
                    $rootScope.to = result;
                });
            };
            $rootScope.processChange = function(){
                var from = $("#from").val();
                var to = $("#to").val();
                var process = $rootScope.selectedProcess;
                if(from == "" || to == "")
                {
                    toastr.info("Please choose the datetime first");
                    return
                }
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
                    $rootScope.get_inspect();
                }
            };
            $rootScope.toCSV = function () {
                var datalist =  $rootScope.datalist;
                if(datalist != null && datalist.length > 0)
                {
                    $rootScope.JSONToCSVConvertor(datalist,'DEFFECT TREND',true);
                }
            };
            $rootScope.JSONToCSVConvertor = function(JSONData, ReportTitle, ShowLabel) {
                //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
                var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
                var CSV = '';
                //Set Report title in first row or line
                CSV += ReportTitle + '\r\n\n';
                //This condition will generate the Label/Header
                if (ShowLabel) {
                    var datelist = $rootScope.datelist;
                    var row = "";
                    row += 'Process' + ',';
                    for (var i = 0; i < datelist.length; i++) {
                        row += '"' + datelist[i] + "" + '",';
                    }
                    row = row.slice(0, -1);
                    //append Label row with line break
                    CSV += row + '\r\n';
                }
                for (var i = 0; i < arrData.length; i++) {
                    var row = "";
                    row += '"' + arrData[i]['name'] + "" + '",';
                    for (var j = 0; j < arrData[i]['data_tb'].length; j++) {
                        row += '"' + arrData[i]['data_tb'][j] + "" + '",';
                    }
                    row.slice(0, row.length - 1);
                    //add a line break after each row
                    CSV += row + '\r\n';
                }

                if (CSV == '') {
                    toastr.info("Invalid data");
                    return;
                }

                //Generate a file name
                var fileName = "";
                //this will remove the blank-spaces from the title and replace it with an underscore
                fileName += ReportTitle.replace(/ /g,"_");

                //Initialize file format you want csv or xls
                var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);

                //this trick will generate a temp <a /> tag
                var link = document.createElement("a");
                link.href = uri;

                //set the visibility hidden so it will not effect on your web-layout
                link.style = "visibility:hidden";
                link.download = fileName + ".csv";

                //this part will append the anchor tag and remove it after automatic click
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };
            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
            $rootScope.initDataType();
            $rootScope.get_tps();
            $rootScope.get_process();
            $rootScope.initSearchDate();
            $rootScope.getTrendData();
        });