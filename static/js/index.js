angular.module("AppModels", [])

.run(
		function($rootScope, $http, $interval, $location) {
			$rootScope.loadModels = function() {
				var url = "/get_models";
				$http.get(url).success(function(result) {
					if(result.length > 0)
					{
						$rootScope.models = result;
						$('#model').show();
						$('#errmsg').hide();
					}
					else
					{
						$('#model').hide();
						$('#errmsg').show();
					}

				});
			};
			$rootScope.openwindow = function(name) {
				var url = "/checkConnection?model=" + name;
				$rootScope.loading = true;
				$http.get(url).success(function(result) {
					$rootScope.loading = false;
					if(result == 'ok')
					{
						window.open('go_ngreport?model=' + name,'_self');
					}else
					{
						toastr.info('Connect to database failed');
					}
				});
			};

			$rootScope.loadModels()

		});
