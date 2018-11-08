angular.module("AppSntracert", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            // get config
            $rootScope.get_configs = function() {
                var from = $("#from").val();
                var to = $("#to").val();
                var url = "/get_configs?model_name=" + $rootScope.model_name + "&from=" + from + "&to=" + to;
                $http.get(url).success(function(result) {
                    if(result == 101)
                    {
                        toastr.info('Connect to database failed')
                        return;
                    }
                    else if(result == 102)
                    {
                        toastr.info('Operate database failed')
                        return;
                    }
                    result.unshift('-');
                    $rootScope.configs = result;
                    $rootScope.selectedConfig = result[0];
                });
            };
            $rootScope.get_lines = function() {
                var url = "/get_lines?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    if(result == 101)
                    {
                        toastr.info('Connect to database failed')
                        return;
                    }
                    else if(result == 102)
                    {
                        toastr.info('Operate database failed')
                        return;
                    }
                    $rootScope.lines = result;
                    $rootScope.selectedLine = result[0]
                    $rootScope.get_datatypeIds()
                });
            };
            // get assy
            $rootScope.get_datatypeIds = function() {
                var url = "/get_datatypeIds?model_name=" + $rootScope.model_name  +
                    "&line=" + $rootScope.selectedLine;
                $http.get(url).success(function(result) {
                    if(result == 101)
                    {
                        toastr.info('Connect to database failed')
                        return;
                    }
                    else if(result == 102)
                    {
                        toastr.info('Operate database failed')
                        return;
                    }
                    $rootScope.datatypeIds = result;
                    $rootScope.selectedDatatype = result[0]
                });
            };

            $rootScope.lineChanged = function() {
                $rootScope.get_datatypeIds();
            };
            $("#from").on("change",function(){
                $rootScope.datetimeChange();
            });
            $("#to").on("change",function(){
                $rootScope.datetimeChange();
            });
            // get rowdata
            $rootScope.datetimeChange = function() {
                // 日期check
                var from = $("#from").val();
                var to = $("#to").val();
                if(from == "" || to == "") {
                    $rootScope.$apply($rootScope.configs = ["-"]);
                    $rootScope.selectedConfig = "-";
                } else {
                    var startTime = new Date(Date.parse(from));
                    var endTime = new Date(Date.parse(to));
                    if (startTime > endTime) {
                        $rootScope.$apply($rootScope.configs = ["-"]);
                        $rootScope.selectedConfig = "-";
                    } else {
                        $rootScope.get_configs();
                    }
                }
            };
            // get rowdata
            $rootScope.get_rowdata = function() {
                $("#doSearch").attr('disabled',true);
                var from = $("#from").val();
                var to = $("#to").val();
                var config = $rootScope.selectedConfig;
                if(config == '-') {
                    config = '';
                }
                $rootScope.perNum = 10;
                var url = "/get_sntracert?model_name=" + $rootScope.model_name
                        + "&from=" + from
                        + "&to=" + to
                        + "&config=" + config
                        + "&pernum=" + $rootScope.perNum
                        + "&line=" + $rootScope.selectedLine
                        + "&datatype_id=" + $rootScope.selectedDatatype
                        + "&mode=" + $rootScope.selectedMode;

                $rootScope.loading = true;
                $http.get(url).success(function(result) {
                    $rootScope.loading = false;
                    $("#doSearch").attr('disabled',false);
                    if(result == 101)
                    {
                        toastr.info('Connect to database failed')
                        return;
                    }
                    else if(result == 102)
                    {
                        toastr.info('Operate database failed')
                        return;
                    }

                    $rootScope.rowdata_serial = result;
                    for (var i = 0; i < result.length; i++) {
                      result[i].copyDetail=[];
                    }
                    $rootScope.expandTable();
                    if ($rootScope.rowdata_serial.length == 0)
                    {
                        toastr.info('Can not find any record!');
                        return;
                    }
                    else
                    {
                        toastr.info('Search Complete!');
                    }
                });
            };
            $rootScope.doSearch = function() {
                var from = $("#from").val();
                var to = $("#to").val();
                if(from == "" || to == "") {
                    toastr.info('Please choose the datetime first')
                } else {
                    var startTime = new Date(Date.parse(from));
                    var endTime = new Date(Date.parse(to));
                    if (startTime > endTime) {
                        toastr.info("Please choose correct datetime")
                    }
                    else {
                        $rootScope.get_rowdata();
                    }
                }
            };
            $rootScope.toCSV = function (val) {
                var datalist =  val.detail;
                if(datalist != null && datalist.length > 0)
                {
                    var filename = $rootScope.selectedLine + "_" + val.process_code;
                    $rootScope.JSONToCSVConvertor(datalist,filename,val,true);
                }
            };
            $rootScope.JSONToCSVConvertor = function(JSONData, ReportTitle, data, ShowLabel) {
                //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
                var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
                var CSV = '';
                //Set Report title in first row or line
                var row = $rootScope.model_name + " SN TRACERT"
                //This condition will generate the Label/Header
                if (ShowLabel) {
                    var datelist = $rootScope.datelist;
                    //append Label row with line break
                    CSV += row + '\r\n';
                    row = "From" + ','
                    row += '"' + $("#from").val().replace("T","  ") + ':00' + '"';
                    CSV += row + '\r\n';
                    row = "To" + ','
                    row += '"' + $("#to").val().replace("T","  ") + ':00' + '"';
                    CSV += row + '\r\n';
                    row = "Config" + ','
                    row += '"' + $rootScope.selectedConfig + '' + '"';
                    CSV += row + '\r\n';
                    row = "Line" + ','
                    row += '"' + $rootScope.selectedLine + '' + '"';
                    CSV += row + '\r\n';
                    row = "OK" + ','
                    row += '"' + data.ok + '' + '"';
                    CSV += row + '\r\n';
                    row = "NG" + ','
                    row += '"' + data.ng + '' + '"';
                    CSV += row + '\r\n';
                    row = "IPQC" + ','
                    row += '"' + data.ipqc + '' + '"';
                    CSV += row + '\r\n';
                    row = "Yield" + ','
                    row += '"' + data.yield + '' + '"';
                    CSV += row + '\r\n';
                    row = "Input" + ','
                    row += '"' + data.input + '' + '"';
                    CSV += row + '\r\n';
                    row = "WIP" + ','
                    row += '"' + data.wip + '' + '"';
                    CSV += row + '\r\n';
                    row = 'Assy Name,Process id,Process Code,Process Name,Serial No.,Result';
                    CSV += row + '\r\n';
                }
                var assy_name = data.assy_name;
                var process_id = data.process_id;
                var process_code = data.process_code;
                var process_name = data.process_name;
                for (var i = 0; i < arrData.length; i++) {
                    row = "";
                    row += '"' + assy_name + '' + '",';
                    row += '"' + process_id + '' + '",';
                    row += '"' + process_code + '' + '",';
                    row += '"' + process_name + '' + '",';
                    row += '"' + arrData[i]['serial_no'] + '' + '",';
                    row += '"' + arrData[i]['result'] + '' + '"';
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
            $rootScope.get_arrow_style = function(val) {
                if (val > 0) {
                    return "table-expandable-arrow"
                } else {
                    return "";
                }
            };
            $rootScope.initButton = function () {
                $('#doSearch').attr('disabled',false);
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
            $rootScope.expandTable = function () {
                $(function () {
                    $('.table-expandable').each(function () {
                        var table = $(this);
                        /*table.children('thead').children('tr').append('<th></th>');*/
                        table.children('tbody').children('tr').filter(':odd').hide();
                        table.children('tbody').children('tr').filter(':even').click(function () {
                            var element = $(this);
                            element.next('tr').toggle('slow');
                            element.find(".table-expandable-arrow").toggleClass("up");
                        });
                        table.children('tbody').children('tr').filter(':even').each(function () {
                            var element = $(this);
                        });
                    });
                });
            };
            $rootScope.initSearch = function () {
                // alert($location.absUrl().split("?")[1].split('#')[0]);
                $rootScope.args = $rootScope.getUrlArgs($location.absUrl().split("?")[1].split('#')[0]);
                $rootScope.model_name = $rootScope.args["model"];
                $rootScope.get_lines();
                $rootScope.initButton();
            };
            // 设置初始日期是当前日期前一夿
            $rootScope.initDate = function () {
                var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
                $http.get(url_date).success(function(result) {
                    $("#from").val(result + 'T00:00');
                    $("#to").val(result + 'T23:59');
                    $rootScope.get_configs();
                });
            };
            // 下一条
            $rootScope.next_p = function (row) {
                row.index = row.index + 1;
                row.s_index = row.index * $rootScope.perNum;
                row.e_index = (row.index+1) * $rootScope.perNum;
                if (row.index!=0){
                    row.first_display=0;
                }else {
                    row.first_display=1;
                }
                if (row.e_index>row.input){
                    row.next_display = 1;
                }else {
                    row.next_display=0;
                }
            };
            // 上一条
            $rootScope.pre_p = function (row) {
                row.index = row.index - 1;
                row.s_index = row.index * $rootScope.perNum;
                row.e_index = (row.index+1) * $rootScope.perNum;
                if (row.index!=0){
                   row.first_display = 0;
                }else {
                    row.first_display = 1;
                }
                 if (row.e_index>row.input){
                    row.next_display = 1;
                }else {
                    row.next_display = 0;
                }
            };
            $rootScope.select_row = function(row) {
                row.copyDetail=row.detail;
            };
            $rootScope.modes = ['INDIVID','LINK'];
            $rootScope.selectedMode = $rootScope.modes[0];
            $rootScope.initSearch();
            $rootScope.initDate();
        });
