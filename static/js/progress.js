angular.module("AppProgress", [])
    .run(function($rootScope, $http, $interval, $location) {
        $rootScope.exits_mplan = function() {
            var url_rate = "/get_Achievement_Rate?model_name=" + $rootScope.model_name;
            var url = "/exits_mplan?model_name=" + $rootScope.model_name;
            var url_date = "/getTodayServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            $http.get(url).success(function(result) {
                if (result == 'false') {
                    if($rootScope.args.hasOwnProperty("date"))
                    {
                        var year = new Date().getFullYear();
                        var month = $rootScope.args['date'].split('/')[0];
                        var day = $rootScope.args['date'].split('/')[1];
                        if(parseInt(month) < 10)
                        {
                            month = '0' + month;
                        }
                        if(parseInt(day) < 10)
                        {
                            day = '0' + day;
                        }
                        var date = year + '-' + month + '-' + day;
                        $("#searchDate").val(date);
                        $rootScope.get_summary(date);
                        $rootScope.get_lineAssy(date);
                        $rootScope.get_lineAssy1(date);
                    }else
                    {
                        $http.get(url_date).success(function(result) {
                            $("#searchDate").val(result);
                            $rootScope.get_summary(result);
                            $rootScope.get_lineAssy(result);
                            $rootScope.get_lineAssy1(result);
                        });
                    }
                }
                else
                {
                    if($rootScope.args.hasOwnProperty("date"))
                    {
                        var year = new Date().getFullYear();
                        var month = $rootScope.args['date'].split('/')[0];
                        var day = $rootScope.args['date'].split('/')[1];
                        if(parseInt(month) < 10)
                        {
                            month = '0' + month;
                        }
                        if(parseInt(day) < 10)
                        {
                            day = '0' + day;
                        }
                        var date = year + '-' + month + '-' + day;
                        $("#searchDate").val(date);
                        $rootScope.get_summary(date);
                        $rootScope.get_lineAssy(date);
                        $rootScope.get_lineAssy1(date);
                    }else
                    {
                        $http.get(url_date).success(function(result) {
                            $("#searchDate").val(result);
                            $rootScope.get_summary(result);
                            $rootScope.get_lineAssy(result);
                            $rootScope.get_lineAssy1(result);
                        });
                    }
                    $rootScope.initButState();
                }
            });
        };
        $rootScope.get_summary = function(date) {
            var url = "/get_summaryDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&time_type=" + $rootScope.time_type;
            $http.get(url).success(function(result) {
                if(result === 102)
                {
                    toastr.info('Operate database failed')
                    return;
                }
                $rootScope.summary_detail = result.summary_detail;
                $rootScope.summary = result.summary;
                $rootScope.initButState();
            });
        };
        $rootScope.get_lineAssy = function(date) {
            var url = "/getProcessDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date ;
            $http.get(url).success(function(result)     {
                if(result === 102)
                {
                    toastr.info('Operate database failed');
                    return;
                }
                $('#diff').show();
                $rootScope.lineAssy = result;
                $rootScope.initButState();
            });
        };
        $rootScope.get_lineAssy1 = function(date) {
            var url = "/getProcessDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&lineNum=1st";
            $http.get(url).success(function(result)     {
                if(result === 102)
                {
                    toastr.info('Operate database failed');
                    return;
                }
                $('#diff').show();
                $rootScope.lineAssy1 = result;
                $rootScope.initButState();
            });
        };

        $rootScope.cell_format = function(val) {
            return (val+ '').replace(/\d{1,3}(?=(\d{3})+(\.\d*)?$)/g, '$&,');
        };
        $rootScope.cell_style = function(val) {
            if (val == '-') {
                return {"background-color" : "#a0a0a0"}
            }
        };
        $rootScope.cell_style_inout = function(v1, v2) {
            if (v1 == '-' || typeof(v1) == "undefined") {
                return {"background-color" : "#a0a0a0"}
            }
            if (v2 == '-' || typeof(v2) == "undefined") {
                return {"background-color" : "#fff"}
            }
            if(time_type == 'All' && $rootScope.flag == true)
            {
                var green = $rootScope.in_out[0];
                var yellow = $rootScope.in_out[1];
                var orange = $rootScope.in_out[2];
                var value = v1/v2*100;
                if (value >= green) {
                    return {"background-color" : "#0f0"}
                } else if ((value >= yellow && value <green)) {
                    return {"background-color" : "#ff0"}
                } else if ((value >= orange && value < yellow)) {
                    return {"background-color" : "#ff7f00"}
                } else if ((value < orange)) {
                    return {
                        "background-color" : "#f00",
                        "color" : "#fff"}
                } else {
                    return {"background-color" : "#fff"}
                }
            }
        };
        $rootScope.cell_style_y2 = function(ay, py) {
            if (ay == '-' || typeof(ay) == "undefined") {
                return {"background-color" : "#a0a0a0"}
            }
            if (py == '-' || typeof(py) == "undefined") {
                return {"background-color" : "#fff"}
            }
            if(time_type == 'All' && $rootScope.flag == true)
            {
                var ay = ay.substring(0, ay.length-1);
                var py = py.substring(0, py.length-1);
                var value = (ay-py);
                var green = $rootScope.yield2[0];
                var white = $rootScope.yield2[1];
                var yellow = $rootScope.yield2[2];
                if (value <= green) {
                    return {"background-color" : "#0f0"}
                } else if ((value >= white && value < yellow)) {
                    return {"background-color" : "#ff0"}
                } else if ((value >= yellow)) {
                    return {"background-color" : "#ff7f00"}
                } else {
                    return {"background-color" : "#fff"}
                }
            }
        };
        $rootScope.initSummaryOffsetData = function () {
            var url = "initSummaryOffsetData?model_name=" + $rootScope.model_name;
            $http.get(url).success(function(result) {
                $rootScope.summaryoffset = result;
            });
        };
        $rootScope.getUrlArgs = function (url) {
            var args = {};
            var items = url.split("&");
            var item = null, name = null, value = null;
            for (var i = 0; i < items.length; i++) {
                item = items[i].split("=");
                name = decodeURIComponent(item[0]);
                value = decodeURIComponent(item[1]);
                args[name] = value;
            }
            return args;
        };
        $rootScope.save = function () {
            var r = /^\+?[1-9][0-9]*$/;
            var csrf = $.cookie('csrftoken');
            var url = "update_summary_offset?model_name=" + $rootScope.model_name + "&csrfmiddlewaretoken=" + csrf;
            for(var p in $rootScope.summaryoffset){
                var flag = r.test($rootScope.summaryoffset[p].ng_count);
                if(flag != true)
                {
                    if(parseInt($rootScope.summaryoffset[p].ng_count) != 0)
                    {
                        toastr.info("Please input positive integer in NG Count.");
                        return
                    }
                }
            }
            $("#save").attr("disabled",true);
            $http({
                method: 'POST',
                url: url,
                data: $rootScope.summaryoffset
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    toastr.info("Update successful");
                }
                else
                {
                    toastr.info("Update failed");
                }
            }, function errorCallback(response) {
                $("#save").attr("disabled",false);
                toastr.info("Update failed");
            });
        };
        $rootScope.initBut = function () {

            $('#save').attr('disabled',true);
        };
        var nowTime=new Date();
        $rootScope.today = nowTime.setTime(nowTime.getTime()-24*60*60*1000);
        $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1].split("#")[0];
        $rootScope.lineAssy = [];
        $rootScope.summary_detail = [];
        $rootScope.startTime = '08:00';
        $rootScope.endTime = '08:00';
        $rootScope.time_type = 'All';
        $rootScope.flag = true;

        $rootScope.getDate = function () {
            var url = "/getServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            if($rootScope.args.hasOwnProperty("date"))
            {
                $rootScope.showDate = $rootScope.args['date'];
            }else
            {
                $http.get(url).success(function(result) {
                    $rootScope.showDate = result;
                });
            }
        };
        $rootScope.getServerDate = function () {
            var url = "/getTodayServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            if($rootScope.args.hasOwnProperty("date"))
            {
                $rootScope.showDate = $rootScope.args['date'];
            }else
            {
                $http.get(url).success(function(result) {
                    $rootScope.serverDate = result;
                    $rootScope.searchDate = result;
                });
            }
        };
        $rootScope.initButState = function () {
            if($rootScope.lineAssy.length > 0 || $rootScope.summary_detail.length > 0)
            {
                $rootScope.butState = false;
            }else
            {
                $rootScope.butState = true;
            }
        };
        $rootScope.timeChange = function ()
        {
            time_type = $rootScope.time_type;
            // var url = "/getStartEndTime?model_name=" + $rootScope.model_name + "&timeType=" + time_type
            // $http.get(url).success(function(result) {
            //     $rootScope.startTime = result[0];
            //     $rootScope.endTime = result[1];
            // });

            if(time_type != 'All')
            {
                $rootScope.startTime = '--:--';
                $rootScope.endTime = '--:--'
            }
            else
            {
                $rootScope.startTime = '08:00';
                $rootScope.endTime = '08:00';
            }
            time_type='All'
        };
        $rootScope.get_summary_time_type = function () {
            var url = "/getSummaryTimeType?model_name=" + $rootScope.model_name;
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

                $rootScope.time_types = result;
                $rootScope.time_type = result[0];
                $rootScope.selectedType = result[0];
            });
        };
        $rootScope.insertFile = function () {
            $('#myModal').modal('toggle');
        };
        $rootScope.exits_mplan();
        $rootScope.getDate();
        $rootScope.getServerDate();
        $rootScope.initBut();
        $rootScope.initButState();
        $rootScope.get_summary_time_type();
        $rootScope.vs_col1_style = function(val) {
            if (val == '-') {
                return {"background-color" : "#a0a0a0"}
            }
        };
        $rootScope.getAutoUpdatings = function () {
            var url = '/getAutoUpdatings?model_name='+$rootScope.model_name;
            $http.get(url).success(function(result) {
                // result = [{'id':1},{'id':2},{'id':3}]
                var res = ['---'];
                for(var i = 0;i < result.length;i ++){
                    res.push(result[i])
                }
                $rootScope.auto_updatings = res;
                $rootScope.auto_updating = res[0];
            });
        };
        $rootScope.autoUpdating = function(){
            if($rootScope.auto_updating == '---'){
                window.location.reload();
            }else{
                var time = $rootScope.auto_updating * 60 * 1000;
                setInterval(function () {
                    $rootScope.exits_mplan();
                    $rootScope.$apply();
                },time);
            }
        };
        $rootScope.getTrendData = function () {
            var url = "get_Trend_Data?model_name=" + $rootScope.model_name;
            $http.get(url).success(function(result)
            {
                $rootScope.trendData = result;
            });
        };
        $rootScope.cellStyle = function (val,tar) {
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
        };
        $rootScope.getAutoUpdatings();
        $rootScope.getTrendData();
    });




