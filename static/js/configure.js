angular.module("AppConfigure", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.initConfigureData = function () {
                var url = "initConfigureData?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    // var assyList = []
                    // var assy = result.assy_text
                    $rootScope.configureData = result
                    $rootScope.expandTable()
                });
            };
            $rootScope.getWorkTime = function () {
                var url = "get_time_tbl_cd?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    $rootScope.worktime = result


                });
            };
            $rootScope.commit = function (data) {
                var line_cd = data.line_cd;
                var url = "get_assytext?model_name=" + $rootScope.model_name + "&line_cd=" + line_cd;
                $http.get(url).success(function(result) {
                    $rootScope.assy_text = result
                });
            };

            $rootScope.save = function () {
                // var jsonstr="[]";
                // var jsonarray = eval('('+jsonstr+')');
                var csrf = $.cookie('csrftoken');
                var url = "update_worktime?model_name=" + $rootScope.model_name + "&csrfmiddlewaretoken=" + csrf;

                // $('#configContent select').each(function () {
                //     if($(this).attr('data-value') != $(this).val())
                //     {
                //         var Line_name = $(this).attr('data-name');
                //         var Assy_Text = $(this).attr('data-text');
                //         var work_time = $(this).val();
                //         jsonarray.push({'Line_name':$(this).attr('data-name'),'Assy_Text':$(this).attr('data-text'),'work_time':$(this).val()});
                //         console.log($(this).attr('data-name'),$(this).attr('data-text'),$(this).attr('data-value'),$(this).val())
                //         // list.attr({'Line_name':$(this).attr('data-name'),'Assy_Text':$(this).attr('data-text'),'work_time':$(this).val()})
                //     }
                // });
                // if(jsonarray != ""){
                    // $http.post(url,jsonarray).success(function(result) {
                    //     alert("SUCCESS")
                    // });

                    $http({
                        method: 'POST',
                        url: url,
                        data: $rootScope.configureData
                    }).then(function successCallback(response) {
                        if(response.data.status == 'success'){
                            alert("Update successful");
                        }
                        else
                        {
                            alert("Update failed");
                        }
                    }, function errorCallback(response) {
                        alert("Update failed");
                    });
                // }
            };
            $rootScope.expandTable = function () {
                $(function () {
                    $('.table-expandable').each(function () {
                        var table = $(this);
                        table.children('thead').children('tr').append('<th></th>');
                        table.children('tbody').children('tr').filter(':odd').hide();
                        table.children('tbody').children('tr').filter(':even').click(function () {
                            var element = $(this);
                            element.next('tr').toggle('slow');
                            element.find(".table-expandable-arrow").toggleClass("up");
                        });
                        table.children('tbody').children('tr').filter(':even').each(function () {
                            var element = $(this);
                            element.append('<td><div class="table-expandable-arrow"></div></td>');
                        });
                    });
                });
            }
            $rootScope.checkbox_disabled = function (value) {
                return value == null
            }
            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
            $rootScope.getWorkTime()
            $rootScope.initConfigureData();
        });