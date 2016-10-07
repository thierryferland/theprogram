var controller = angular.module('epicprog.controller.signinbutton', []);

controller.controller('epicprog.controller.signinbutton', ['$scope', '$rootScope', '$state', '$auth', '$mdDialog', '$mdMedia', 'epicApiRequest',
function signinCtl($scope, $rootScope, $state, $auth, $mdDialog, $mdMedia, epicApiRequest) {

	$scope.logout = function() {
		if (!$auth.isAuthenticated()) {
			return;
		}
		$auth.logout().then(function() {
			$scope.islogin = false;
			$state.go('demo');
		});
	};

	$scope.login = function(ev) {
		if ($auth.isAuthenticated()) {
			$scope.logout();
		} else {
			var useFullScreen = ($mdMedia('sm') || $mdMedia('xs')) && $rootScope.customFullscreen;
			$mdDialog.show({
				controller : 'epicprog.controller.login',
				templateUrl : 'templates/login.html',
				targetEvent : ev,
				clickOutsideToClose : true,
				fullscreen : useFullScreen
			});
		}
	};

	$scope.getUser = function() {
		params = {};
		epicApiRequest.executeAuth('balance', 'user.get', params, 'GET').then(function(resp) {
			if (!resp.code) {
				$scope.data.profilepic = resp.data.picture;
			}
		}).catch(function(resp) {

		});
	};

	$scope.data = {
		profilepic : 'images/ic_person_24px.svg'
	};

	if ($auth.isAuthenticated()) {
		$scope.getUser();
	}
}]); 