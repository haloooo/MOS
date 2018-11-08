angular.module("AppNgreport", [])
    .run(function ($rootScope, $http, $interval, $location) {
        $rootScope.exits_mplan = function () {
            var url_rate = "/get_Achievement_Rate?model_name=" + $rootScope.model_name;
            var url = "/exits_mplan?model_name=" + $rootScope.model_name;
            var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            $http.get(url_rate).success(function (result) {
                console.log(result[0]['in_out']);
                console.log(result[0]['yield2']);
                $rootScope.in_out = result[0]['in_out'];
                $rootScope.yield2 = result[0]['yield2']
            });
            $http.get(url).success(function (result) {
                if (result == 'false') {
                    if ($rootScope.args.hasOwnProperty("date")) {
                        var year = new Date().getFullYear();
                        var month = $rootScope.args['date'].split('/')[0];
                        var day = $rootScope.args['date'].split('/')[1];
                        if (parseInt(month) < 10) {
                            month = '0' + month;
                        }
                        if (parseInt(day) < 10) {
                            day = '0' + day;
                        }
                        var date = year + '-' + month + '-' + day;
                        $("#searchDate").val(date);
                        $rootScope.get_summary(date);
                        $rootScope.get_summary1(date);
                        $rootScope.get_lineAssy(date);
                        $rootScope.get_lineAssy1(date);
                    } else {
                        $http.get(url_date).success(function (result) {
                            $("#searchDate").val(result);
                            $rootScope.get_summary(result);
                            $rootScope.get_summary1(result);
                            $rootScope.get_lineAssy(result);
                            $rootScope.get_lineAssy1(result);
                        });
                    }
                }
                else {
                    if ($rootScope.args.hasOwnProperty("date")) {
                        var year = new Date().getFullYear();
                        var month = $rootScope.args['date'].split('/')[0];
                        var day = $rootScope.args['date'].split('/')[1];
                        if (parseInt(month) < 10) {
                            month = '0' + month;
                        }
                        if (parseInt(day) < 10) {
                            day = '0' + day;
                        }
                        var date = year + '-' + month + '-' + day;
                        $("#searchDate").val(date);
                        $rootScope.get_summary(date);
                        $rootScope.get_summary1(date);
                        $rootScope.get_lineAssy(date);
                        $rootScope.get_lineAssy1(date);
                    } else {
                        $http.get(url_date).success(function (result) {
                            $("#searchDate").val(result);
                            $rootScope.get_summary(result);
                            $rootScope.get_summary1(result);
                            $rootScope.get_lineAssy(result);
                            $rootScope.get_lineAssy1(result);
                        });
                    }
                    $rootScope.initButState();
                }
            });
        };

        $rootScope.get_summary = function (date) {
            var url = "/get_summaryDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&time_type=" + $rootScope.time_type + "&lineNum=2nd";
            $http.get(url).success(function (result) {
                if (result == 102) {
                    toastr.info('Operate database failed')
                    return
                }
                $rootScope.summary_detail = result.summary_detail;
                $rootScope.summary = result.summary;
                $rootScope.initButState();
            });
        };
        $rootScope.get_summary1 = function (date) {
            var url = "/get_summaryDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&time_type=" + $rootScope.time_type + "&lineNum=1st";
            $http.get(url).success(function (result) {
                if (result == 102) {
                    toastr.info('Operate database failed')
                    return
                }
                $rootScope.summary_detail1 = result.summary_detail;
                $rootScope.summary1 = result.summary;
                $rootScope.initButState();
            });
        };
        $rootScope.get_lineAssy = function (date) {
            var url = "/get_lineSummaryDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&time_type=" + $rootScope.time_type + "&lineNum=2nd";
            $http.get(url).success(function (result) {
                if (result === 102) {
                    toastr.info('Operate database failed')
                    return;
                }
                $rootScope.lineAssy = result;
                $rootScope.initButState();
            });
        };
        $rootScope.get_lineAssy1 = function (date) {
            var url = "/get_lineSummaryDetail?model_name=" + $rootScope.model_name + "&searchDate=" + date + "&time_type=" + $rootScope.time_type + "&lineNum=1st";
            $http.get(url).success(function (result) {
                if (result === 102) {
                    toastr.info('Operate database failed')
                    return;
                }
                $rootScope.lineAssy1 = result;
                $rootScope.initButState();
            });
        };


        $rootScope.cell_format = function (val) {
            return (val + '').replace(/\d{1,3}(?=(\d{3})+(\.\d*)?$)/g, '$&,');
        };
        $rootScope.cell_style = function (val) {
            if (val === '-') {
                return {"background-color": "#a0a0a0"};
            }
        };
        $rootScope.cell_style_inout = function (v1, v2) {
            if (v1 === '-' || typeof(v1) === "undefined") {
                return {"background-color": "#a0a0a0"};
            }
            if (v2 === '-' || typeof(v2) === "undefined") {
                return {"background-color": "#fff"};
            }
            if (time_type === 'All' && $rootScope.flag === true) {
                var green = $rootScope.in_out[0];
                var yellow = $rootScope.in_out[1];
                var orange = $rootScope.in_out[2];
                var value = v1 / v2 * 100;
                if (value >= green) {
                    return {"background-color": "#0f0"};
                } else if ((value >= yellow && value < green)) {
                    return {"background-color": "#ff0"};
                } else if ((value >= orange && value < yellow)) {
                    return {"background-color": "#ff7f00"};
                } else if ((value < orange)) {
                    return {
                        "background-color": "#f00",
                        "color": "#fff"
                    };
                } else {
                    return {"background-color": "#fff"};
                }
            }
        };
        $rootScope.cell_style_y2 = function (ay, py) {
            if (ay === '-' || typeof(ay) === "undefined") {
                return {"background-color": "#a0a0a0"};
            }
            if (py === '-' || typeof(py) === "undefined") {
                return {"background-color": "#fff"};
            }
            if (time_type === 'All' && $rootScope.flag === true) {
                var ay = ay.substring(0, ay.length - 1);
                var py = py.substring(0, py.length - 1);
                var value = (ay - py);
                var green = $rootScope.yield2[0];
                var white = $rootScope.yield2[1];
                var yellow = $rootScope.yield2[2];
                if (value <= green) {
                    return {"background-color": "#0f0"};
                } else if ((value >= white && value < yellow)) {
                    return {"background-color": "#ff0"};
                } else if ((value >= yellow)) {
                    return {"background-color": "#ff7f00"};
                } else {
                    return {"background-color": "#fff"};
                }
            }
        };
        $rootScope.initSummaryOffsetData = function () {
            var url = "initSummaryOffsetData?model_name=" + $rootScope.model_name;
            $http.get(url).success(function (result) {
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
            for (var p in $rootScope.summaryoffset) {
                var flag = r.test($rootScope.summaryoffset[p].ng_count);
                if (flag !== true) {
                    if (parseInt($rootScope.summaryoffset[p].ng_count) !== 0) {
                        toastr.info("Please input positive integer in NG Count.");
                        return;
                    }
                }
            }
            $("#save").attr("disabled", true);
            $http({
                method: 'POST',
                url: url,
                data: $rootScope.summaryoffset
            }).then(function successCallback(response) {
                if (response.data.status === 'success') {
                    toastr.info("Update successful");
                }
                else {
                    toastr.info("Update failed");
                }
            }, function errorCallback(response) {
                $("#save").attr("disabled", false);
                toastr.info("Update failed");
            });
        };
        $rootScope.initBut = function () {

            $('#save').attr('disabled', true);
        };
        var nowTime = new Date();
        $rootScope.today = nowTime.setTime(nowTime.getTime() - 24 * 60 * 60 * 1000);
        $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1].split("#")[0];
        $rootScope.lineAssy = [];
        $rootScope.summary_detail = [];
        $rootScope.startTime = '08:00';
        $rootScope.endTime = '08:00';
        $rootScope.time_type = 'All';
        $rootScope.flag = true;
        var time_type = 'All'
        $rootScope.getDate = function () {
            var url = "/getServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            if ($rootScope.args.hasOwnProperty("date")) {
                $rootScope.showDate = $rootScope.args["date"];
            } else {
                $http.get(url).success(function (result) {
                    $rootScope.showDate = result;
                });
            }
        };
        $rootScope.getServerDate = function () {
            var url = "/getFullServerDate?model_name=" + $rootScope.model_name;
            $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
            if ($rootScope.args.hasOwnProperty("date")) {
                $rootScope.showDate = $rootScope.args['date'];
            } else {
                $http.get(url).success(function (result) {
                    $rootScope.serverDate = result;
                    $rootScope.searchDate = result;
                });
            }
        };
        $rootScope.initButState = function () {
            if ($rootScope.lineAssy.length > 0 || $rootScope.summary_detail.length > 0) {
                $rootScope.butState = false;
            } else {
                $rootScope.butState = true;
            }
        };
        $rootScope.toSearch = function () {

            var searchDate = $("#searchDate").val();
            if (searchDate == "") {
                toastr.info("Please choose the datetime first");
                return
            }
            if ($rootScope.time_type != 'All') {
                $rootScope.flag = false;
            }
            else {
                $rootScope.flag = true;
            }
            var temp = searchDate.split("-");
            var showDate = temp[1] + '/' + temp[2];
            $rootScope.showDate = showDate;
            console.log($rootScope.showDate);
            $rootScope.searchDate = searchDate;
            $rootScope.get_summary(searchDate);
            $rootScope.get_summary1(searchDate);
            $rootScope.get_lineAssy(searchDate);
            $rootScope.get_lineAssy1(searchDate);
            toastr.info('search complete');
        };
        $rootScope.timeChange = function () {
            time_type = $rootScope.time_type;
            // var url = "/getStartEndTime?model_name=" + $rootScope.model_name + "&timeType=" + time_type
            // $http.get(url).success(function(result) {
            //     $rootScope.startTime = result[0];
            //     $rootScope.endTime = result[1];
            // });

            if (time_type != 'All') {
                $rootScope.startTime = '--:--';
                $rootScope.endTime = '--:--'
            }
            else {
                $rootScope.startTime = '08:00';
                $rootScope.endTime = '08:00';
            }
            time_type = 'All'
        };
        $rootScope.get_summary_time_type = function () {
            var url = "/getSummaryTimeType?model_name=" + $rootScope.model_name;
            $http.get(url).success(function (result) {
                if (result == 101) {
                    toastr.info('Connect to database failed');
                    return
                }
                else if (result == 102) {
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
        $rootScope.upload = function () {
            // 后缀判定
            var filepath = $("input[name='fileUpload']").val();
            if (filepath == "") {
                toastr.info("Please select the file first");
                return false;
            }
            var extStart = filepath.lastIndexOf(".");
            var ext = filepath.substring(extStart, filepath.length).toUpperCase();
            if (ext != ".XLS" && ext != ".XLSX" && ext != ".XLSM" && ext != ".XLSB") {
                toastr.info("The files are limited to XLS, XLSX, XLSM, XLSB format");
                return false;
            }
            var file = document.getElementById("fileUpload").files[0];
            var csrf = $.cookie('csrftoken');
            var fd = new FormData();
            fd.append("csrfmiddlewaretoken", csrf);
            fd.append("file", file);
            fd.append("model_name", $rootScope.model_name);
            $.ajax({
                type: "POST",
                data: fd,
                url: "upload",
                contentType: false,
                processData: false,
                success: function (data) {
                    str = data.substring(0, 13);
                    if (str == 'Please ensure') {
                        toastr.info(adata);
                        $('#myModal').modal('hide')
                    }
                    else {
                        $rootScope.msg = 'No data of the previous day!';
                        var jsonObj = eval('(' + data + ')');
                        for (var i = 0; i < jsonObj.length; i++) {
                            if ($rootScope.serverDate == jsonObj[i].Date) {
                                $rootScope.msg = '';
                                break
                            }
                        }
                        for (var key in jsonObj[0]) {
                            if (key == 'before_quantity') {
                                $rootScope.plan_1 = $.parseJSON(data);
                                $rootScope.$apply();
                                $('#myModal2').modal('toggle')
                            }
                            else if (key == 'in_quantity') {
                                $rootScope.plan_2 = $.parseJSON(data);
                                $rootScope.$apply();
                                $('#myModal3').modal('toggle')
                            }
                        }

                    }
                },
                error: function (data) {
                    toastr.info("Please contact the administrator");
                }
            });
        };
        //insert database
        $rootScope.insert = function () {
            $("#insert").attr("disabled", true);
            var file = document.getElementById("fileUpload").files[0];
            var csrf = $.cookie('csrftoken');
            var fd = new FormData();
            fd.append("csrfmiddlewaretoken", csrf);
            fd.append("file", file);
            fd.append("model_name", $rootScope.model_name);
            $.ajax({
                type: "POST",
                data: fd,
                url: "insertDatabase",
                contentType: false,
                processData: false,
                success: function (data) {
                    $("#insert").attr("disabled", false);
                    var obj = eval('(' + data + ')');
                    if (obj.status == 'success') {
                        toastr.info("Importing database success");
                    }
                    else {
                        toastr.info("Importing database fail");
                    }
                    $('#myModal').modal('hide');
                    $('#myModal2').modal('hide');
                    $('#myModal3').modal('hide');
                },
                error: function () {
                    $("#insert").attr("disabled", false);
                    toastr.info("Importing database fail");
                    $('#myModal').modal('hide');
                    $('#myModal2').modal('hide');
                }
            });
        };
        //cancel
        $rootScope.cancel = function (val) {
            if (val == 'upload') {
                $('#myModal').modal('hide');
                $('#myModal2').modal('hide');
                $('#myModal3').modal('hide');

            }
            else {
                $('#myModal2').modal('hide');
                $('#myModal3').modal('hide');

            }
        };
        $rootScope.vs_col1_style = function (val) {
            if (val == '-') {
                return {"background-color": "#a0a0a0"}
            }
        };

        $rootScope.getTrendData = function () {
            var url = "get_Trend_Data?model_name=" + $rootScope.model_name;
            $http.get(url).success(function (result) {
                $rootScope.trendData = result;
            });
        };
        $rootScope.cellStyle = function (val, tar) {
            if (val === 'NP') {
                return {"background-color": "#00FF00"};
            }
            else {
                var red = $rootScope.trendData[0];
                var orange = $rootScope.trendData[1];
                var num = val.replace('%', '');
                val = parseFloat(num) / 100;
                if (val >= tar) {
                    return {"background-color": "#00FF00"};
                }
                else if (val >= tar - orange && val < tar) {
                    return {"background-color": "#FFFF00"};
                }
                else if (val >= tar - red && val < tar - orange) {
                    return {"background-color": "#FFC000"};
                }
                else if (val < tar - red) {
                    return {"background-color": "#FF0000"};
                }
                else {
                    return {"background-color": "#00FF00"};
                }
            }
        };
        $rootScope.getTrendData();
        $rootScope.toCSV = function () {
            $rootScope.SummaryToCSV($rootScope.summary1,$rootScope.summary_detail1,'Summary_First', true);
            $rootScope.SummaryToCSV($rootScope.summary,$rootScope.summary_detail,'Summary_Second', true);
            $rootScope.AssyToCSV($rootScope.lineAssy,'Line_Assy_Second',true);
            $rootScope.AssyToCSV($rootScope.lineAssy1,'Line_Assy_First',true);
        };

        $rootScope.SummaryToCSV = function(summary, summary_detail, excel_name, ShowLabel){
            if (summary_detail.length > 0) {
                $rootScope.JSONToCSVConvertor_Summary(summary, summary_detail, excel_name, ShowLabel);
            }
            // $('#Assytable').tableExport({type: 'csv', escape: 'false'});
        };

        $rootScope.AssyToCSV = function(lineAssy, excel_name, ShowLabel){
            if (lineAssy.length > 0) {
                $rootScope.JSONToCSVConvertor_Assy(lineAssy, excel_name, ShowLabel);
            }
        };

        $rootScope.JSONToCSVConvertor_Summary = function (summaryDate, JSONData, ReportTitle, ShowLabel) {
            //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
            var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
            var CSV = '';
            //Set Report title in first row or line
            CSV += ReportTitle + '\r\n\n';
            //This condition will generate the Label/Header
            if (ShowLabel) {
                var row = "";
                row += 'Assy' + ',';
                row += 'Plan_In' + ',';
                row += 'Plan_Out' + ',';
                row += 'Plan_Yield' + ',';
                row += 'Before' + ',';
                row += 'Actual_In' + ',';
                row += 'Actual_out' + ',';
                row += 'Actual_Yield(Y2)' + ',';
                row += 'Actual_Yield(Y1)' + ',';
                row += 'Y2-Y1' + ',';
                row += 'After' + ',';
                row += 'NG' + ',';
                row = row.slice(0, -1);
                //append Label row with line break
                CSV += row + '\r\n';
            }
            for (var i = 0; i < arrData.length; i++) {
                var row = "";
                row += '"' + arrData[i]['assy'] + "" + '",';
                row += '"' + arrData[i]['plan_in'] + "" + '",';
                row += '"' + arrData[i]['plan_out'] + "" + '",';
                row += '"' + arrData[i]['plan_yield'] + "" + '",';
                row += '"' + arrData[i]['before'] + "" + '",';
                row += '"' + arrData[i]['actual_in'] + "" + '",';
                row += '"' + arrData[i]['actual_out'] + "" + '",';
                row += '"' + arrData[i]['actual_y2'] + "" + '",';
                row += '"' + arrData[i]['actual_y1'] + "" + '",';
                row += '"' + arrData[i]['y2_y1'] + "" + '",';
                row += '"' + arrData[i]['after'] + "" + '",';
                row += '"' + arrData[i]['ng'] + "" + '",';
                row.slice(0, row.length - 1);
                //add a line break after each row
                CSV += row + '\r\n';
            }
            CSV += '\r\n';
            row = "";
            row += '"' + 'Assembly Yield1(sub+main)' + "" + '",';
            row += '"' + summaryDate['y1_fpy_sub'] + "" + '",';
            row += '"' + 'Assembly Yield2(sub+main)' + "" + '",';
            row += '"' + summaryDate['y2_fpy_sub'] + "" + '",';
            // row += '"' + 'y1y2_fpy_sub' + "" + '",';
            // row += '"' + summaryDate['y1y2_fpy_sub'] + "" + '",';
            CSV += row + '\r\n';

            row = "";
            row += '"' + 'Assy Yield1(main)' + "" + '",';
            row += '"' + summaryDate['y1_assembly_yield_sub'] + "" + '",';
            row += '"' + 'Assy Yield2(main)' + "" + '",';
            row += '"' + summaryDate['y2_assembly_yield_sub'] + "" + '",';
            // row += '"' + 'y1y2_assembly_yield_sub' + "" + '",';
            // row += '"' + summaryDate['y1y2_assembly_yield_sub'] + "" + '",';
            CSV += row + '\r\n';

            row = "";
            row += '"' + 'FPY1(sub+main)' + "" + '",';
            row += '"' + summaryDate['y1_fpy'] + "" + '",';
            row += '"' + 'FPY2(sub+main)' + "" + '",';
            row += '"' + summaryDate['y2_fpy'] + "" + '",';
            // row += '"' + 'y1y2_fpy' + "" + '",';
            // row += '"' + summaryDate['y1y2_fpy'] + "" + '",';
            CSV += row + '\r\n';

            row = "";
            row += '"' + 'FPY1(main)' + "" + '",';
            row += '"' + summaryDate['y1_assembly_yield'] + "" + '",';
            row += '"' + 'FPY2(main)' + "" + '",';
            row += '"' + summaryDate['y2_assembly_yield'] + "" + '",';
            // row += '"' + 'y1y2_assembly_yield' + "" + '",';
            // row += '"' + summaryDate['y1y2_assembly_yield'] + "" + '",';
            CSV += row + '\r\n';

            row = "";
            row += '"' + 'before_summary' + "" + '",';
            row += '"' + summaryDate['before_summary'] + "" + '",';
            row += '"' + 'after_summary' + "" + '",';
            row += '"' + summaryDate['after_summary'] + "" + '",';
            CSV += row + '\r\n';
            if (CSV == '') {
                toastr.info("Invalid data");
                return;
            }

            //Generate a file name
            var fileName = "";
            //this will remove the blank-spaces from the title and replace it with an underscore
            fileName += ReportTitle.replace(/ /g, "_");

            //Initialize file format you want csv or xls
            var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);

            // Now the little tricky part.
            // you can use either>> window.open(uri);
            // but this will not work in some browsers
            // or you will not get the correct file extension

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
        $rootScope.JSONToCSVConvertor_Assy = function (JSONData, ReportTitle, ShowLabel) {
            //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
            var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
            var CSV = '';
            //Set Report title in first row or line
            CSV += ReportTitle + '\r\n\n';
            for (var i = 0; i < arrData.length; i++) {
                var row = "";
                if(i == 0){
                    for(var j in arrData[i]['data']){
                        row += '"",';
                        for(var k = 0; k < arrData[i]['data'][j].length-1; k++){
                            if(parseInt(j)==0){
                                row += '"' + arrData[i]['data'][j][k] + "" + '",';
                                row += '"",';
                            }else{
                                row += '"' + arrData[i]['data'][j][k] + "" + '",';
                            }
                        }
                        CSV += row + '\r\n';
                        row = '';
                    }
                }else{
                    for(var j in arrData[i]['data']){
                        if(parseInt(j)==0){
                            row += '"' + arrData[i]['name'] + "" + '",';
                        }else{
                            row += '"",';
                        }
                        for(var k = 0; k < arrData[i]['data'][j].length-1; k++){
                            row += '"' + arrData[i]['data'][j][k] + "" + '",';
                        }
                        CSV += row + '\r\n';
                        row = '';
                    }
                }
                // row += '"' + arrData[i]['plan_in'] + "" + '",';
                // row += '"' + arrData[i]['plan_out'] + "" + '",';
                // row += '"' + arrData[i]['plan_yield'] + "" + '",';
                // row += '"' + arrData[i]['before'] + "" + '",';
                // row += '"' + arrData[i]['actual_in'] + "" + '",';
                // row += '"' + arrData[i]['actual_out'] + "" + '",';
                // row += '"' + arrData[i]['actual_y2'] + "" + '",';
                // row += '"' + arrData[i]['actual_y1'] + "" + '",';
                // row += '"' + arrData[i]['y2_y1'] + "" + '",';
                // row += '"' + arrData[i]['after'] + "" + '",';
                // row += '"' + arrData[i]['ng'] + "" + '",';
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
            fileName += ReportTitle.replace(/ /g, "_");

            //Initialize file format you want csv or xls
            var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);

            // Now the little tricky part.
            // you can use either>> window.open(uri);
            // but this will not work in some browsers
            // or you will not get the correct file extension

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
        }

    });




