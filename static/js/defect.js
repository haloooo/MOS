var app = angular.module("AppDefect", []);
app.run(
    function($rootScope, $http, $interval, $location) {
        $rootScope.get_lines = function() {
            $("#Content").hide();
            var url = "/get_lines?model_name=" + $rootScope.model_name;
            $http.get(url).success(function(result) {
                if(result == 101)
                {
                    toastr.info('Connect to database failed')
                    return
                }
                else if(result == 102)
                {
                    toastr.info('Operate database failed')
                    return
                }
                result.push('All Line');
                $rootScope.lines = result;
                $rootScope.selectedLine = result[0];
                $rootScope.get_assys()
            });
        };
        //get top rank
        $rootScope.getTopRank = function () {
            var url = "/get_toprank?model_name=" + $rootScope.model_name;
            $http.get(url).success(function(result) {
                $rootScope.topRanks = result;
                $rootScope.selectedRank = result[0];
            });
        };
        // get assy
        $rootScope.get_assys = function() {
            var url = "/get_assys?model_name=" + $rootScope.model_name  +
                "&line=" + $rootScope.selectedLine;
            $http.get(url).success(function(result) {
                if(result == 101)
                {
                    toastr.info('Connect to database failed')
                    return
                }
                else if(result == 102)
                {
                    toastr.info('Operate database failed')
                    return
                }
                result.push('All Assy');
                $rootScope.assys = result;
                $rootScope.selectedAssy = result[0];
                $rootScope.get_tps()
            });
        };
        // get Time Part
        $rootScope.get_tps = function() {
            var url = "/get_tps?model_name=" + $rootScope.model_name  +"&line=" + $rootScope.selectedLine
                + "&assy=" + $rootScope.selectedAssy;
            $http.get(url).success(function(result) {
                if(result == 101)
                {
                    toastr.info('Connect to database failed')
                    return
                }
                else if(result == 102)
                {
                    toastr.info('Operate database failed')
                    return
                }
                $rootScope.tps = result;
                $rootScope.selectedTp = result[0]
            });
        };
        $rootScope.toCSV = function () {
            var inspect_info =  $rootScope.inspect_info;
            if(inspect_info != null && inspect_info.length > 0)
            {
                $rootScope.JSONToCSVConvertor(inspect_info,'DEFECT',true);
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
                var row = "";
                row += 'No' + ',';
                row += 'Ng_Inspect' + ',';
                row += 'Process' + ',';
                row += 'Assy' + ',';
                row += 'Input' + ',';
                row += 'Failed' + ',';
                row += 'Detractor' + ',';
                row += 'Yield' + ',';
                row += 'Cum' + ',';
                row = row.slice(0, -1);
                //append Label row with line break
                CSV += row + '\r\n';
            }
            for (var i = 0; i < arrData.length; i++) {
                var row = "";
                row += '"' + (i + 1) + "" + '",';
                row += '"' + arrData[i]['NG_Inspect'] + "" + '",';
                row += '"' + arrData[i]['Process'] + "" + '",';
                row += '"' + arrData[i]['Assy'] + "" + '",';
                row += '"' + arrData[i]['Input'] + "" + '",';
                row += '"' + arrData[i]['Failed'] + "" + '",';
                row += '"' + arrData[i]['Detractor'] + "%" + '",';
                row += '"' + arrData[i]['Yield'] + "%" + '",';
                row += '"' + arrData[i]['Cum'] + "%" + '",';
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
        $rootScope.lineChanged = function() {
            $rootScope.get_assys()
        };
        $rootScope.assyChanged = function() {
            $rootScope.get_tps()
        };
        //do search
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
                var searchUrl = "search_defect?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to +
                    "&line=" + $rootScope.selectedLine + "&assy=" + $rootScope.selectedAssy +
                    "&time_part=" + $rootScope.selectedTp['time_part'] + "&top_rank=" + $rootScope.selectedRank +
                    "&target=" + $rootScope.selectedTarget + "&mode=" + $rootScope.selectedMode    ;
                $("#search").attr("disabled",true);
                $("#exportFile").attr("disabled",true);
                if($rootScope.selectedMode == "Pareto")
                {
                    $http.get(searchUrl).success(function(result)
                    {
                        $("#search").attr("disabled",false);
                        if(result.length == 0)
                        {
                            toastr.info('Can not find any record!');
                            $("#search").attr("disabled",false);
                            return
                        }else {
                            // Export Data disabled false
                            $("#exportFile").attr('disabled',false);
                            for (var i = 0, l = result.length; i < l; i++) {
                                for (var key in result[i]) {
                                    if (key == 'status') {
                                        toastr.info('Query error in server!');
                                        $("#search").attr("disabled", false);
                                        return
                                    }
                                }
                            }
                        }
                        var xA = result.x;
                        var chart = {
                            zoomType: 'xy'
                        };
                        var subtitle = {
                            text: ''
                        };
                        var title = {
                            text: 'Pareto Chart'
                        };

                        var xAxis = {
                            categories: xA,
                            crosshair: true,
                            labels:{
                                rotation:-45,
                                step:1
                            }
                        };

                        var yAxis= [{ // 第一条Y轴
                            labels: {
                                format: '{value}PCS',
                                style: {
                                    color: Highcharts.getOptions().colors[1]
                                }
                            },
                            title: {
                                text: '',
                                style: {
                                    color: Highcharts.getOptions().colors[1]
                                }
                            }
                        }, { // 第二条Y轴
                            // max:100,
                            // min:10,
                            tickPositions:[0,33,66,100],
                            title: {
                                text: '',
                                style: {
                                    color: Highcharts.getOptions().colors[0]
                                }
                            },
                            labels: {
                                format: '{value}%',
                                style: {
                                    color: Highcharts.getOptions().colors[0]
                                }
                            },
                            opposite: true
                        }];
                        var tooltip = {
                            shared: true
                        };
                        var legend = {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            x: 0,
                            y: 20,
                            borderWidth: 0,
                        };
                        var credits = { enabled: false };
                        var exporting = {
                            enabled:false
                        };
                        var series= [{
                            name: 'Failed',
                            type: 'column',
                            data: result.y_left,
                            tooltip: {
                                valueSuffix: 'PCS'
                            }

                        }, {
                            name: 'Cum',
                            type: 'spline',
                            yAxis: 1,
                            data: result.y_right,
                            color:'orange',
                            tooltip: {
                                valueSuffix: '%'
                            }
                        }
                        ];
                        var json = {};
                        json.chart = chart;
                        json.title = title;
                        json.subtitle = subtitle;
                        json.xAxis = xAxis;
                        json.yAxis = yAxis;
                        json.tooltip = tooltip;
                        json.legend = legend;
                        json.series = series;
                        json.credits = credits;
                        json.exporting = exporting;
                        // json.scrollbar = scrollbar;
                        $('#container').highcharts(json);
                        $rootScope.col = ['Failed','-NG_Inspect'];//默认按Failed列降序+NG_Inspect列升序排序
                        $rootScope.desc = 1;//默认排序条件升序
                        $rootScope.inspect_info = result.inspect_info;
                        $("#Content").show();
                    });
                }
                else
                {
                    $http.get(searchUrl).success(function(result)
                    {
                        $("#search").attr("disabled",false);
                        if(result.length == 0)
                        {
                            toastr.info('can not find any record!');
                            $("#search").attr("disabled",false);
                            return
                        }else {
                            $("#exportFile").attr('disabled',false);
                            for (var i = 0, l = result.length; i < l; i++) {
                                for (var key in result[i]) {
                                    if (key == 'status') {
                                        toastr.info('query error in server!');
                                        $("#search").attr("disabled", false);
                                        return
                                    }
                                }
                            }
                        }
                        var xA = result.x;
                        var chart = {
                            zoomType: 'xy'
                        };
                        var subtitle = {
                            text: ''
                        };
                        var title = {
                            text: 'Yield Bridge'
                        };

                        var xAxis = {
                            categories: xA,
                            crosshair: true,
                            labels:{
                                rotation:-45,
                                step:1
                            }
                        };
                        var yAxis= [{ // 第一条Y轴
                            labels: {
                                format: '{value}%',
                                style: {
                                    color: Highcharts.getOptions().colors[1]
                                }
                            },
                            // tickPositions:[0,33,66,100],
                            title: {
                                text: '',
                                style: {
                                    color: Highcharts.getOptions().colors[1]
                                }
                            }
                        }, { // 第二条Y轴
                            // max:100,
                            // min:10,
                            tickPositions:[0,33,66,100],
                            title: {
                                text: '',
                                style: {
                                    color: Highcharts.getOptions().colors[0]
                                }
                            },
                            labels: {
                                format: '{value}%',
                                style: {
                                    color: Highcharts.getOptions().colors[0]
                                }
                            },
                            opposite: true
                        }];
                        var tooltip = {
                            shared: true
                        };
                        var legend = {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom',
                            x: 0,
                            y: 20,
                            borderWidth: 0,
                        };
                        var credits = { enabled: false };
                        var exporting = {
                            enabled:false
                        };
                        var series= [{
                            name: 'Detractor',
                            type: 'column',
                            data: result.y_left,
                            tooltip: {
                                valueSuffix: '%'
                            }

                        }, {
                            name: 'Cum',
                            type: 'spline',
                            yAxis: 1,
                            data: result.y_right,
                            color:'orange',
                            tooltip: {
                                valueSuffix: '%'
                            }
                        }
                        ];
                        var json = {};
                        json.chart = chart;
                        json.title = title;
                        json.subtitle = subtitle;
                        json.xAxis = xAxis;
                        json.yAxis = yAxis;
                        json.tooltip = tooltip;
                        json.legend = legend;
                        json.series = series;
                        json.credits = credits;
                        json.exporting = exporting;
                        $('#container').highcharts(json);
                        $rootScope.col = ['Detractor','-Cum'];//默认按Detractor列降序+Cum列升序排序
                        $rootScope.desc = 1;//默认排序条件升序
                        $rootScope.inspect_info = result.inspect_info;
                        $("#Content").show();
                    });
                }

            }
        };
        $rootScope.ng_inspect = function () {
            if($('#Ng_Inspect1').is(':hidden')){
                $rootScope.initPic();
                $('#Ng_Inspect1').show();
                $('#Ng_Inspect2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Ng_Inspect1').hide();
                $('#Ng_Inspect2').show();
            }
        };
        $rootScope.Process = function () {
            if($('#Process1').is(':hidden')){
                $rootScope.initPic();
                $('#Process1').show();
                $('#Process2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Process1').hide();
                $('#Process2').show();
            }
        };
        $rootScope.Assy = function () {
            if($('#Assy1').is(':hidden')){
                $rootScope.initPic();
                $('#Assy1').show();
                $('#Assy2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Assy1').hide();
                $('#Assy2').show();
            }
        };
        $rootScope.Input = function () {
            if($('#Input1').is(':hidden')){
                $rootScope.initPic();
                $('#Input1').show();
                $('#Input2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Input1').hide();
                $('#Input2').show();
            }
        };
        $rootScope.Failed = function () {
            if($('#Failed1').is(':hidden')){
                $rootScope.initPic();
                $('#Failed1').show();
                $('#Failed2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Failed1').hide();
                $('#Failed2').show();
            }
        };
        $rootScope.Detractor = function () {
            if($('#Detractor1').is(':hidden')){
                $rootScope.initPic();
                $('#Detractor1').show();
                $('#Detractor2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Detractor1').hide();
                $('#Detractor2').show();
            }
        };
        $rootScope.Yield = function () {
            if($('#Yield1').is(':hidden')){
                $rootScope.initPic();
                $('#Yield1').show();
                $('#Yield2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Yield1').hide();
                $('#Yield2').show();
            }
        };
        $rootScope.Cum = function () {
            if($('#Cum1').is(':hidden')){
                $rootScope.initPic();
                $('#Cum1').show();
                $('#Cum2').hide();
            }
            else
            {
                $rootScope.initPic();
                $('#Cum1').hide();
                $('#Cum2').show();
            }
        };
        $rootScope.initTable = function (tableId)
        {
            $("#" + tableId).dataTable({
                'ordering':true
            });
        };
        $rootScope.initPic = function () {
            $('#Ng_Inspect2').hide();
            $('#Process2').hide();
            $('#Assy2').hide();
            $('#Input2').hide();
            $('#Failed2').hide();
            $('#Detractor2').hide();
            $('#Yield2').hide();
            $('#Cum2').hide();
            $('#Ng_Inspect1').show();
            $('#Process1').show();
            $('#Assy1').show();
            $('#Input1').show();
            $('#Failed1').show();
            $('#Detractor1').show();
            $('#Yield1').show();
            $('#Cum1').show()
        };
        $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
        $rootScope.selectedDate = '';
        $rootScope.targets = ['Inspect','Serial'];
        $rootScope.selectedTarget = $rootScope.targets[0];
        $rootScope.modes = ['Pareto','Yield'];
        $rootScope.selectedMode = $rootScope.modes[0];
        $rootScope.initDate = function () {
            var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
            $http.get(url_date).success(function(result) {
                $("#from").val(result);
                $("#to").val(result);
            });
            // Export Data disabled
            $("#exportFile").attr('disabled',true);
        };
        $rootScope.initDate();
        $rootScope.get_lines();
        $rootScope.getTopRank();
        $rootScope.initPic();
    });