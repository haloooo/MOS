angular.module("AppAssy", [])

    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.initAssyData = function () {
                var url = "initAssyData?model_name=" + $rootScope.model_name;
                $http.get(url).success(function(result) {
                    $rootScope.assy = result
                });
            };

            $rootScope.update = function (result) {
                $rootScope.item = result;
                $("#assy_text").val(result.assy_text);
                $('#myModal').modal('toggle')
            };

            $rootScope.commit = function (result) {
                var assy_text = $("#assy_text").val();
                var spacecheck = /\s/ig;
                var assy_text_back = assy_text.replace(spacecheck, "");
                if (assy_text_back == '')
                {
                    alert('Please Input Assy Text.');
                    return;
                }
                $http({
                    method: 'GET',
                    url: "update_assy?model_name=" + $rootScope.model_name +"&process_id=" + result.process_id + "&assy_text=" + assy_text,
                }).then(function successCallback(response) {
                    result.assy_text = assy_text;
                }, function errorCallback(response) {
                    alert("Update failed!");
                });
                $('#myModal').modal('hide')
            };

            $rootScope.cancel = function (result) {
                $('#myModal').modal('hide')
            };

            $rootScope.model_name = $location.absUrl().split("?")[1].split("=")[1];
            $rootScope.initAssyData()
        });