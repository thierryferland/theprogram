var controller = angular.module('epicprog.controller.login', []);

controller.controller('epicprog.controller.login', ['$scope', '$auth', '$state','$mdDialog', '$rootScope',
    function loginCtl($scope, $auth, $state, $mdDialog, $rootScope) {

		$scope.authenticate = function(provider) {
	        $auth.authenticate(provider).then(function(response){
	        	$rootScope.token = response.data.token;
	        	$mdDialog.hide();
	        	$rootScope.islogin = true;
	        	$state.go('add');
	        })
	        .catch(function(error) {
	          if (error.error) {
	            // Popup error - invalid redirect_uri, pressed cancel button, etc.
	          } else if (error.data) {
	            // HTTP response error from server
	          } else {
	          }
	        });	
		};
    }
]);