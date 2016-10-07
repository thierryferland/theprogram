var controller = angular.module('epicprog.controller.signup', []);

controller.controller('epicprog.controller.signup', ['$scope', '$auth', '$state','$mdDialog', '$rootScope',
    function signupCtl($scope, $auth, $state, $mdDialog, $rootScope) {

		$scope.authenticate = function(provider) {
	        $auth.authenticate(provider).then(function(response){
	        	$rootScope.token = response.data.token;
	        	$rootScope.islogin = true;
	        	$state.go('setup');
	        })
	        .catch(function(error) {
	          if (error.error) {
	            // Popup error - invalid redirect_uri, pressed cancel button, etc.
	            console.log(error.error);
	          } else if (error.data) {
	            // HTTP response error from server
	            console.log(error.data);
	          } else {
	          	console.log(error);
	          }
	        });	
		};
    }
]);