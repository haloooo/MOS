angular.module("AppChart", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.search = function () {
                var from = $("#from").val();
                var to = $("#to").val();
                if(from == "" || to == "")
                {
                    alert("Please choose the datetime first")
                    return
                }
                var arr = [],i=0;
                var start = from;
                var end = to;
                var startTime = new Date(Date.parse(from));
                var endTime = new Date(Date.parse(to));
                if(startTime > endTime)
                {
                    alert("Please choose correct datetime")
                }else
                {
                    var startTime = $rootScope.getDate(start);
                    var endTime = $rootScope.getDate(end);
                    while((endTime.getTime()-startTime.getTime())>=0){
                        var year = startTime.getFullYear();
                        var month = (startTime.getMonth()+1).toString().length==1?"0"+(startTime.getMonth()+1).toString():(startTime.getMonth()+1).toString();
                        var day = startTime.getDate().toString().length==1?"0"+startTime.getDate():startTime.getDate();
                        arr[i]=year+"-"+month+"-"+day;
                        startTime.setDate(startTime.getDate()+1);
                        i+=1;
                    }
                    var AdverseRateurl = "search_AdverseRate?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to;
                    var NgUrl = "search_Ng?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to;
                    var OkUrl = "search_Ok?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to;
                    $("#search").attr("disabled",true);
                    $http({
                        method: 'GET',
                        url: AdverseRateurl
                    }).then(function successCallback(result) {
                        chart = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'AdverseRate',
                                    type: 'line',
                                    zoomType: 'x'
                                },
                                title: {
                                    text: 'Daily Yield Trend',
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
                                    plotLines: [{
                                        value: 0,
                                        width: 1,
                                        color: '#808080'
                                    }]
                                },
                                tooltip: {
                                    xDateFormat: '%Y-%m-%d %H:%M:%S',
                                    shared: true
                                },
                                legend: {
                                    layout: 'vertical',
                                    align: 'right',
                                    verticalAlign: 'top',
                                    x: -10,
                                    y: 0,
                                    borderWidth: 0
                                },
                                series: result.data
                            });
                    }, function errorCallback(result) {
                        console.log("get AdverseRate data failed!");
                    });
                    $http({
                        method: 'GET',
                        url: NgUrl
                    }).then(function successCallback(result) {
                        chart = new Highcharts.Chart({
                            chart: {
                                renderTo: 'Ng',
                                type: 'column',
                                zoomType: 'x'
                            },
                            title: {
                                text: 'Daily NG Trend',
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
                                plotLines: [{
                                    value: 0,
                                    width: 1,
                                    color: '#808080'
                                }]
                            },
                            tooltip: {
                                xDateFormat: '%Y-%m-%d %H:%M:%S',
                                shared: true
                            },
                            legend: {
                                layout: 'vertical',
                                align: 'right',
                                verticalAlign: 'top',
                                x: -10,
                                y: 0,
                                borderWidth: 0
                            },
                            series: result.data
                        });
                    }, function errorCallback(result) {
                        console.log("get Ng data failed!");
                    });
                    $http({
                        method: 'GET',
                        url: OkUrl
                    }).then(function successCallback(result) {
                        $("#search").attr("disabled",false);
                        chart = new Highcharts.Chart({
                            chart: {
                                renderTo: 'Ok',
                                type: 'column',
                                zoomType: 'x'
                            },
                            title: {
                                text: 'Daily OK Trend',
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
                                plotLines: [{
                                    value: 0,
                                    width: 1,
                                    color: '#808080'
                                }]
                            },
                            tooltip: {
                                xDateFormat: '%Y-%m-%d %H:%M:%S',
                                shared: true
                            },
                            legend: {
                                layout: 'vertical',
                                align: 'right',
                                verticalAlign: 'top',
                                x: -10,
                                y: 0,
                                borderWidth: 0
                            },
                            series: result.data
                        });
                    }, function errorCallback(result) {
                        $("#search").attr("disabled",false);
                        console.log("get Ok data failed!");
                    });
                }
            };
            $rootScope.getDate = function(datestr){
                var temp = datestr.split("-");
                var date = new Date(temp[0],temp[1]-1,temp[2]);
                console.log(date);
                return date;
            };
            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
        });