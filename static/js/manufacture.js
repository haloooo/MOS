angular.module("AppManufacture", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.get_lines = function() {
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
                    $rootScope.lines = result;
                    if( $rootScope.args && $rootScope.args.hasOwnProperty("line")){
                        $rootScope.selectedLine = $rootScope.args["line"]
                    }else{
                        $rootScope.selectedLine = result[0]
                    }
                    $rootScope.get_assys()
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
                    $rootScope.assys = result;
                    if($rootScope.args &&  $rootScope.args.hasOwnProperty("assy")){
                        $rootScope.selectedAssy = $rootScope.args["assy"]
                    }else{
                        $rootScope.selectedAssy = result[0]
                    }
                    $rootScope.get_tps()
                });
            };
            // get Time Part
            $rootScope.get_tps = function() {
                var time_part = $rootScope.args["time_type"];
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
                    for(var i = 0;i<result.length;i++)
                    {
                        var obj = result[i];
                        if(obj.time_part.indexOf('D01') != -1)
                        {
                            $rootScope.selectedTp = obj;
                            break;
                        }
                        else
                        {
                            $rootScope.selectedTp = result[0];
                            break;
                        }
                    }

                    if($rootScope.args && $rootScope.args.hasOwnProperty("time_type"))
                    {
                        for(var i = 0;i<result.length;i++)
                        {
                            var obj = result[i];
                            if(obj.time_part.indexOf($rootScope.args["time_type"]) != -1)
                            {
                                $rootScope.selectedTp = obj;
                                break;
                            }
                        }
                    }
                    if($rootScope.args && $rootScope.args.hasOwnProperty("line")){
                        $rootScope.doSearch();
                        $rootScope.args = null;
                    }
                });
            };

            $rootScope.lineChanged = function() {
                $rootScope.get_assys()
            };
            $rootScope.assyChanged = function() {
                $rootScope.get_tps()
            };
            $rootScope.tpChanged = function() {
                //$rootScope.selectedTp
                // for (tp in $rootScope.tps) {
                // 	if (tp.time_part == $rootScope.selectedTp) {
                // 		$rootScope.selectedTs = tp.time_val_s
                // 		$rootScope.selectedTe = tp.time_val_e
                // 		break;
                // 	}
                // }
            };
            // get rowdata
            $rootScope.get_rowdata = function() {
                $("#doSearch").attr('disabled',true);
                var selectedModel = $('#selectedModel').val();
                try
                {
                    var url = "/get_1_processdetail?model_name=" + $rootScope.model_name
                        +"&line=" + $rootScope.selectedLine
                        +"&assy=" + $rootScope.selectedAssy
                        + "&process_at="+ $rootScope.selectedDate
                        + "&time_part="+ $rootScope.selectedTp.time_part
                        + "&selectedModel=" + selectedModel;
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
                        if(selectedModel == 'Serial')
                        {
                            $("#inspect").hide();
                            $('#serial').show();
                            $('#summary').show();
                            $rootScope.rowdata_serial = result;
                            $rootScope.doSummary($rootScope.rowdata_serial, "First");
                        }
                        else if(selectedModel == 'Inspect')
                        {
                            $("#inspect").show();
                            $('#serial').hide();
                            $('#summary').hide();
                            $rootScope.rowdata_inspect = result;
                        }
                        $rootScope.get_rowdata2()
                    });
                }
                catch (err)
                {
                    toastr.info('Can not find such Assy in m_work table');
                }

            };
            // get rowdata2
            $rootScope.get_rowdata2 = function() {
                var selectedModel = $('#selectedModel').val();
                var url = "/get_2_processdetail?model_name=" + $rootScope.model_name
                    +"&line=" + $rootScope.selectedLine
                    +"&assy=" + $rootScope.selectedAssy
                    + "&process_at="+ $rootScope.selectedDate
                    + "&time_part="+ $rootScope.selectedTp.time_part
                    + "&selectedModel=" + selectedModel;
                $http.get(url).success(function(result) {
                    $("#doSearch").attr('disabled',false);
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
                    if(selectedModel == 'Serial')
                    {
                        $("#inspect2").hide();
                        $('#serial2').show();
                        $('#summary2').show();
                        $rootScope.rowdata2_serial = result;
                        $rootScope.doSummary($rootScope.rowdata2_serial,"Second");
                        $rootScope.expandTable();
                    }
                    else if(selectedModel == 'Inspect')
                    {
                        $("#inspect2").show();
                        $('#serial2').hide();
                        $('#summary2').hide();
                        $rootScope.rowdata2_inspect = result;
                        $rootScope.expandTable();
                    }
                    if(selectedModel == 'Serial')
                    {
                        if ($rootScope.rowdata_serial.length == 0 && $rootScope.rowdata2_serial.length == 0)
                        {
                            // $rootScope.toast('Can not find any record!');
                            toastr.info('Can not find any record!');
                        }
                        else
                        {
                            // $rootScope.toast('Search Complete!');
                            toastr.info('Search Complete!');
                        }
                    }
                    else if(selectedModel == 'Inspect')
                    {
                        if ($rootScope.rowdata_inspect.length == 0 && $rootScope.rowdata2_inspect.length == 0)
                        {
                            // $rootScope.toast('Can not find any record!');
                            toastr.info('Can not find any record!');
                        }
                        else
                        {
                            // $rootScope.toast('Search Complete!');
                            toastr.info('Search Complete!');
                        }
                    }
                });
            };

            // summary
            $rootScope.doSummary = function(rowdata,flg) {
                var input_c = 0;
                var output_c = 0;
                var ng_c = 0;
                var input_i = -1;
                for (var i in rowdata) {
                    if (rowdata[i].ok > 0 && input_i == -1) {
                        input_i = i
                        input_c = rowdata[i].ok + rowdata[i].ng
                    }
                    if (rowdata[i].ok > 0) {
                        output_c = rowdata[i].ok
                    }
                    //if (i ==0) {
                    //    input_c = rowdata[i].ok + rowdata[i].ng
                    //}
                    //if (i ==rowdata.length - 1) {
                    //    output_c = rowdata[i].ok
                    //}
                    ng_c = ng_c + rowdata[i].ng
                }
                if (rowdata.length > 0) {
                    yield = 0
                    if ((output_c+ ng_c) > 0) {
                        yield = output_c/(output_c + ng_c)
                    }
                    if (flg == 'First') {
                        $rootScope.summary1 = {'input':input_c,'output':output_c,'yield':(yield * 100).toFixed(2) + '%'}
                    } else {
                        $rootScope.summary2 = {'input':input_c,'output':output_c,'yield':(yield * 100).toFixed(2) + '%'}
                    }
                } else {
                    if (flg == 'First') {
                        $rootScope.summary1 = {}
                    } else {
                        $rootScope.summary2 = {}
                    }
                }
            };
            // get detail
            $rootScope.get_detail = function(data_seq, inspect_cd) {
                var url = "/get_1_defectdetail?model_name=" + $rootScope.model_name  +"&data_seq=" + data_seq +
                    "&inspect_cd="+ inspect_cd;
                $http.get(url).success(function(result) {
                    $rootScope.detail = result;
                });
            };
            $rootScope.get_detail2 = function(data_seq, inspect_cd) {
                var url = "/get_2_defectdetail?model_name=" + $rootScope.model_name  +"&data_seq=" + data_seq +
                    "&inspect_cd="+ inspect_cd;
                $http.get(url).success(function(result) {
                    $rootScope.detail2 = result;
                });
            };
            $rootScope.doSearch = function() {
                if ($rootScope.selectedDate == '') {
                    toastr.info('Please choose the datetime first')
                } else {
                    $rootScope.get_rowdata();
                }
            };
            $rootScope.get_arrow_style = function(val) {
                if (val > 0) {
                    return "table-expandable-arrow"
                } else {
                    return ""
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
                $('#serial').hide();
                $('#serial2').hide();
                if($rootScope.args.hasOwnProperty("line")){
                    $rootScope.selectedDate = $rootScope.args["day"];
                    if($rootScope.args["line"]=="all"){
                        $rootScope.getFirstLine();
                        return false;
                    }
                }
                else
                {
                    var url_date = "/getFullServerDate?model_name=" + $rootScope.model_name;
                    $http.get(url_date).success(function(result) {
                        $rootScope.selectedDate = result;
                    });
                }
                $rootScope.get_lines();
                $rootScope.initButton();
            };

            $rootScope.getFirstLine = function () {
                var url = "/getLine?model_name=" + $rootScope.model_name  +"&assy=" +  $rootScope.args["assy"];
                $http.get(url).success(function(result) {
                    $rootScope.args["line"] = result;
                    $rootScope.get_lines();
                    $rootScope.initButton();
                });
            };
            $rootScope.initSearch();
            // $rootScope.selectedDate = '';
        });
