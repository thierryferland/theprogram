var controller = angular.module('epicprog.controller.usercards', []);
	
controller.controller('epicprog.controller.usercards', ['$scope', '$state','$mdDialog','$mdMedia', '$mdToast', 'epicApiRequest',
    function usercardCtl($scope, $state, $mdDialog, $mdMedia, $mdToast, epicApiRequest) {
	
    	/**
    	 * Get status
    	 */
    	$scope.getFollowedUsers = function() {
    		epicApiRequest.executeAuth('balance','pot.getFollowedUsers', params, 'GET').then(function(resp) {
    							if (!resp.code) {
    								$scope.users = resp.data.summaries;
    							}
    						})
				.catch(function(resp) {
								//$state.go('demo');
    						});
    	};
    	
    	/**
    	 * Push notify the user
    	 */
    	 $scope.pushNotify = function() {
			params = {
    			'user_nickname' : user_nickname
    		};
			user_nickname = this.user_status.username;
        	epicApiRequest.executeAuth('balance','user.push_notify', params, 'POST').then(function(resp) {
    			if (!resp.code) {
    				$scope.popup_message = "Notification sent";
					ngDialog.open({
                        template: 'popupMoney',
                        className: 'ngdialog-theme-default',
                        scope: $scope,
                        showClose: false
                    });
    			}
    		});
	    };

		$scope.showStats = function(ev,userStatus) {

		    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
		    $mdDialog.show({
		      controller: 'epicprog.controller.histo',
		      templateUrl: 'templates/histo.html',
		      //parent: angular.element(document.body),
		      targetEvent: ev,
		      clickOutsideToClose:true,
		      fullscreen: useFullScreen,
		      locals: {
			      userStatus: userStatus
			  }
		    });

		  };

    	$scope.getFollowedUsers();
    }
]);