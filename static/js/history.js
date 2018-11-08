angular.module("AppHistory", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.get_lines = function () {
                var url = "/get_lines?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
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
                    result.push('All Line');
                    $rootScope.lines = result;
                    $rootScope.selectedLine = result[0];
                });
            };
            $rootScope.init = function () {
                $("#main").hide();
            };
            $rootScope.doSearch = function () {
                if($rootScope.selectedDataType !== 'Yield(Y2)')
                {
                    $rootScope.flag = false;
                }
                else
                {
                    $rootScope.flag = true;
                }
                var arr = [],i=0;
                var from = $("#from").val();
                var to = $("#to").val();
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
                    var startTime = $rootScope.getDate(start);
                    var endTime = $rootScope.getDate(end);
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
                    if(arr.length > 31)
                    {
                        toastr.info('The number of query days is more than 31 days');
                        return;
                    }
                    var Object = $rootScope.selectedObj;
                    var Content = $rootScope.selectedLine;
                    var DataType = $rootScope.selectedDataType;
                    if(DataType === "Yield(Y1)")
                    {
                        DataType = 'Y1';
                    }else if(DataType === 'Yield(Y2)')
                    {
                        DataType = 'Y2';
                    }
                    var url = "search_history?model_name=" + $rootScope.model_name + "&object=" + Object + "&content=" + Content + "&dataType=" + DataType + "&from=" + from + "&to=" + to;
                    $("#search").attr("disabled",true);
                    $("#exportFile").attr("disabled",true);
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
                        // var data = [{'process':'Inner Assy','yield2':[99.99,0.00]},{'process':'Inner','yield2':[99.99,0.00]}];
                        if(result.length == 0)
                        {
                            toastr.info('Can not find any record!');
                            $("#search").attr("disabled",false);
                            return
                        }else
                        {
                            for(var i = 0,l = result.length;i<l;i++)
                            {
                                for(var key in result[i])
                                {
                                    if(key == 'status')
                                    {
                                        $("#target").hide();
                                        toastr.info('query error in server!');
                                        $("#search").attr("disabled",false);
                                        return;
                                    }
                                }
                            }
                            $rootScope.datelist = arr;
                            $rootScope.datalist = result;
                            for(var i in result){
                                console.log(result[i])
                            }
                            if(Object === 'Assy')
                            {
                                document.getElementById('title').innerText=Content;
                            }
                            else
                            {
                                document.getElementById('title').innerText='Assy';
                            }
                            $("#search").attr("disabled",false);
                            $("#exportFile").attr('disabled',false);
                            $("#main").show();
                            $("#target").show();
                            toastr.info('search complete');
                        }
                    });
                }
            };
            $rootScope.toCSV = function () {
                var datalist =  $rootScope.datalist;
                if(datalist != null && datalist.length > 0)
                {
                    $rootScope.JSONToCSVConvertor(datalist,'TREND',true);
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
                    row += 'Assy' + ',';
                    for (var i = 0; i < datelist.length; i++) {
                        row += '"' + datelist[i] + "" + '",';
                    }
                    row = row.slice(0, -1);
                    //append Label row with line break
                    CSV += row + '\r\n';
                }
                for (var i = 0; i < arrData.length; i++) {
                    var row = "";
                    row += '"' + arrData[i]['process'] + "" + '",';
                    for (var j = 0; j < arrData[i]['data'].length; j++) {
                        row += '"' + arrData[i]['data'][j] + "" + '",';
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
            $rootScope.getDate = function(datestr){
                var temp = datestr.split("-");
                var date = new Date(temp[0],temp[1]-1,temp[2]);
                console.log(date);
                return date;
            };
            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
            $rootScope.get_history_targrt = function () {
                var url = "get_history_targrt?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result)
                {
                    $rootScope.target = result;
                });
            };
            $rootScope.get_history_assy = function () {
                var url = "get_history_assy?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result)
                {
                    $rootScope.assy = result;
                });
            };
            $rootScope.cell_style_red = function (val,tar) {
                var red = $rootScope.trendData[0];
                var num = val.replace('%','');
                val = parseFloat(num)/100;
                if(dataType === 'Yield(Y2)' && $rootScope.flag === true){
                    if(val < tar-red)
                    {
                        return {"color" : "white"};
                    }else
                    {
                        return {"color" : "black"};
                    }
                }else{
                    return {"color" : "black"};
                }
            };
            $rootScope.cell_style = function (val,tar) {
                var target = $rootScope.target;
                var assy = $rootScope.assy;
                if(dataType === 'Yield(Y2)' && $rootScope.flag === true){
                    if(val === 'NP')
                    {
                        return {"background-color" : "#00FF00"};
                    }
                    else
                    {
                        var red = $rootScope.trendData[0];
                        var orange = $rootScope.trendData[1];
                        var num = val.replace('%','');
                        val = parseFloat(num)/100;
                        if(val >= tar)
                        {
                            return {"background-color" : "#00FF00"};
                        }
                        else if( val >= tar-orange && val < tar)
                        {
                            return {"background-color" : "#FFFF00"};
                        }
                        else if( val >= tar-red && val < tar-orange)
                        {
                            return {"background-color" : "#FFC000"};
                        }
                        else if(val < tar-red)
                        {
                            return {"background-color" : "#FF0000"};
                        }
                        else
                        {
                            return {"background-color" : "#00FF00"};
                        }
                    }
                }
            };
            $rootScope.getTrendData = function () {
                var url = "get_Trend_Data?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result)
                {
                    $rootScope.trendData = result;
                });
            };
            $rootScope.getTrendDataColor = function () {
                var url = "get_Trend_DataColor?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result)
                {
                    $rootScope.trendDataColor = result;
                });
            };
            $rootScope.initDate = function () {
                var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
                $http.get(url_date).success(function(result) {
                    $("#from").val(result);
                    $("#to").val(result);
                });
                // Export Data disabled
                $("#exportFile").attr('disabled',true);
            };
            $rootScope.initObj = function () {
                var url = "/getObjs?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    $rootScope.objects = result;
                    $rootScope.selectedObj = result[0];
                });
            };
            $rootScope.initDataType = function () {
                var url = "/getDataType?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    $rootScope.dataTypes = result;
                    $rootScope.selectedDataType = result[0];
                });
            };
            $rootScope.objChange = function () {
                if($rootScope.selectedObj === 'Line'){
                    $rootScope.get_lines();
                }else if ($rootScope.selectedObj === 'Assy'){
                    $rootScope.get_assys();
                }
            };
            // get assy
            $rootScope.get_assys = function() {
                var url = "/get_assys?model_name=" + $rootScope.model_name  +
                    "&line=All Line";
                $http.get(url).success(function(result) {
                    if(result === 101)
                    {
                        toastr.info('Connect to database failed');
                        return;
                    }
                    else if(result === 102)
                    {
                        toastr.info('Operate database failed');
                        return;
                    }
                    $rootScope.lines = result;
                    $rootScope.selectedLine = result[0];
                });
            };
            $rootScope.flag = true;
            var dataType = 'Yield(Y2)';
            $rootScope.initDate();
            $rootScope.get_lines();
            $rootScope.getTrendData();
            $rootScope.getTrendDataColor();
            $rootScope.init();
            $rootScope.get_history_targrt();
            $rootScope.get_history_assy();
            $rootScope.initObj();
            $rootScope.initDataType();
        });

