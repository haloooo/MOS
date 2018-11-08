angular.module("AppUpload", [])
    .run(function($rootScope, $http, $interval, $location) {
        var nowTime=new Date();
        $rootScope.today = nowTime.setTime(nowTime.getTime()-24*60*60*1000);
        $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1].split("#")[0];
        $rootScope.lineAssy = [];
        $rootScope.summary_detail = [];
        $rootScope.startTime = '08:00';
        $rootScope.endTime = '08:00';
        $rootScope.time_type = 'All';
        $rootScope.initUploadData = function () {
            $rootScope.initSummaryOffsetData();
        };
        $rootScope.initSummaryOffsetData = function () {
            var url = "initSummaryOffsetData?model_name=" + $rootScope.model_name;
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
                $rootScope.summaryoffset = result;
            });
        };
        $rootScope.save = function () {
            var r = /^\+?[1-9][0-9]*$/;
            // var r = /.*\..*/;
            var csrf = $.cookie('csrftoken');
            var url = "update_summary_offset?model_name=" + $rootScope.model_name + "&csrfmiddlewaretoken=" + csrf;
            for(var p in $rootScope.summaryoffset){
                var flag = r.test($rootScope.summaryoffset[p].ng_count);
                if(flag != true)
                {
                    // alert(parseInt($rootScope.summaryoffset[p].ng_count));
                    if($rootScope.summaryoffset[p].ng_count != 0 || $rootScope.summaryoffset[p].ng_count != '0')
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
        $rootScope.insertFile = function () {
            $('#myModal').modal('toggle');
        };
        $rootScope.initBut = function () {
            $('#save').attr('disabled',true);
        };
        $rootScope.upload = function(){
            // 后缀判定
            var filepath=$("input[name='fileUpload']").val();
            if (filepath==""){
                toastr.info("Please select the file first");
                return false;
            }
            var extStart=filepath.lastIndexOf(".");
            var ext=filepath.substring(extStart,filepath.length).toUpperCase();
            if(ext!=".XLS"&&ext!=".XLSX"&&ext!=".XLSM"&&ext!=".XLSB"){
                toastr.info("The files are limited to XLS, XLSX, XLSM, XLSB format");
                return false;
            }
            var file = document.getElementById("fileUpload").files[0];
            var csrf = $.cookie('csrftoken');
            var fd = new FormData();
            fd.append("csrfmiddlewaretoken", csrf);
            fd.append("file", file);
            fd.append("model_name",$rootScope.model_name)
            $.ajax({
                type: "POST",
                data: fd,
                url: "upload",
                contentType: false,
                processData: false,
                success: function (data)
                {
                    str = data.substring(0, 13);
                    if(str == 'Please ensure')
                    {
                        toastr.info(data);
                        $('#myModal').modal('hide')
                    }
                    else
                    {
                        $rootScope.msg = 'No data of the previous day!';
                        var jsonObj = eval('(' + data + ')');
                        for(var i=0; i<jsonObj.length; i++){
                            if($rootScope.serverDate == jsonObj[i].Date)
                            {
                                $rootScope.msg = '';
                                break
                            }
                        }
                        for(var key in jsonObj[0])
                        {
                            if(key == 'before_quantity')
                            {
                                $rootScope.plan_1 = $.parseJSON(data);
                                $rootScope.$apply();
                                $('#myModal2').modal('toggle')
                            }
                            else if(key == 'in_quantity')
                            {
                                $rootScope.plan_2 = $.parseJSON(data);
                                $rootScope.$apply();
                                $('#myModal3').modal('toggle')
                            }
                        }

                    }
                },
                error: function (data)
                {
                    toastr.info("Please contact the administrator");
                }
            });
        };
        //insert database
        $rootScope.insert = function(){
            $("#insert").attr("disabled",true);
            var file = document.getElementById("fileUpload").files[0];
            var csrf = $.cookie('csrftoken');
            var fd = new FormData();
            fd.append("csrfmiddlewaretoken", csrf);
            fd.append("file", file);
            fd.append("model_name",$rootScope.model_name);
            $.ajax({
                type: "POST",
                data: fd,
                url: "insertDatabase",
                contentType: false,
                processData: false,
                success: function (data)
                {
                    $("#insert").attr("disabled",false);
                    var obj = eval('(' + data + ')');
                    if(obj.status == 'success')
                    {
                        toastr.info("Importing database success");
                        // $rootScope.get_summary();
                        // $rootScope.get_lineAssy();
                        // $rootScope.initSummaryOffsetData();
                    }
                    else
                    {
                        toastr.info("Importing database fail");
                    }
                    $('#myModal').modal('hide');
                    $('#myModal2').modal('hide');
                    $('#myModal3').modal('hide');
                },
                error: function ()
                {
                    $("#insert").attr("disabled",false);
                    toastr.info("Importing database fail");
                    $('#myModal').modal('hide');
                    $('#myModal2').modal('hide');
                }
            });
        };
        //cancel
        $rootScope.cancel = function (val) {
            if(val == 'upload')
            {
                $('#myModal').modal('hide');
                $('#myModal2').modal('hide');
                $('#myModal3').modal('hide');

            }
            else
            {
                $('#myModal2').modal('hide');
                $('#myModal3').modal('hide');

            }
        };
        $rootScope.getServerDate = function () {
            var url = "/getFullServerDate?model_name=" + $rootScope.model_name;
            $http.get(url).success(function(result) {
                $rootScope.serverDate = result;
            });
        };
        $rootScope.getServerDate();
        $rootScope.initUploadData();
        $rootScope.initBut();

    });




