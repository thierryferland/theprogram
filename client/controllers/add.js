var controller = angular.module('epicprog.controller.add', []);
	
controller.controller('epicprog.controller.add', ['$scope', '$state','$mdDialog','$mdMedia', '$mdToast', 'epicApiRequest',
    function addCtl($scope, $state, $mdDialog, $mdMedia, $mdToast, epicApiRequest) {
	
    	/**
    	 * Adds a drink
    	 */
    	$scope.addDrink = function(increment) {
    		$scope.current_user.had_today =	Math.max($scope.current_user.had_today + increment,0);
    	};   	
    	
    	/**
    	 * Sends the number of drinks for one day
    	 */
    	$scope.redeemBadges = function() {
    		var message = 'Sending drinks';
    		$scope.showToast(message);
    		$scope.ready = false;
    		params = {'end_date.year' : $scope.data.date.getFullYear(),
				'end_date.month' : $scope.data.date.getMonth() + 1,
				'end_date.day' : $scope.data.date.getDate(),
				'nDrinks' : $scope.current_user.had_today};
    		epicApiRequest.executeAuth('balance','user.redeemBadges', params, 'POST').then(function(resp) {
    			if (!resp.code) {
					//$scope.current_user = resp.data;
					$scope.showAlert(null,resp.data.badges);
    				$scope.ready = true;
    				$scope.getStatus();
    				$scope.getFollowedUsers();
    			}
    		});
    	};
    	
    	/**
    	 * Get status
    	 */
    	$scope.getStatus = function() {
    		params = {'date.year' : $scope.data.date.getFullYear(),
				'date.month' : $scope.data.date.getMonth() + 1,
				'date.day' : $scope.data.date.getDate()};
    		epicApiRequest.executeAuth('balance','pot.getStatus', params, 'GET').then(function(resp) {
    							if (!resp.code) {
    								$scope.ready = true;
    								$scope.current_user = resp.data;
    							}
    						})
				.catch(function(resp) {
								$state.go('demo');
    						});
    	};
    	
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
    	 * Change date
    	 */
    	 $scope.changeDate = function(increment) {
    	 	$scope.ready = false;
    	 	$scope.data.date.setDate($scope.data.date.getDate() + increment);
    	 	$scope.data.datelabel = $scope.data.weekdays[$scope.data.date.getDay()].name + ", " + $scope.data.availableMonth[$scope.data.date.getMonth()].name + " " + $scope.data.availableDay[$scope.data.date.getDate()-1].name;
			$scope.getStatus();	    
	    };
		    	
    	function init_form() {
    		var yesterday = new Date();
    		yesterday.setDate(yesterday.getDate() - 1);
    		var weekday = yesterday.getDay();
    		var yesterday_day = yesterday.getDate();
    		var yesterday_month = yesterday.getMonth()+1;
    		var yesterday_year = yesterday.getFullYear();
			
			$scope.data.selectedWeekday = yesterday.getDay();
			$scope.data.date = yesterday; 
			$scope.data.datelabel = $scope.data.weekdays[weekday].name + ", " + $scope.data.availableMonth[yesterday_month-1].name + " " + $scope.data.availableDay[yesterday_day-1].name;
    	}
    	
		$scope.showAlert = function(ev,badges) {
		    // Appending dialog to document.body to cover sidenav in docs app
		    // Modal dialogs should fully cover application
		    // to prevent interaction outside of dialog
		    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
		    $mdDialog.show({
		      controller: 'epicprog.controller.badges',
		      templateUrl: 'templates/badges.html',
		      targetEvent: ev,
		      clickOutsideToClose:true,
		      fullscreen: useFullScreen,
		      locals: {
			      badges: badges
			  }
		    });
		  };
		
		$scope.showToast = function(message) {
		    $mdToast.show(
		      $mdToast.simple()
		        .textContent(message)
		        .position("top right")
		        .hideDelay(3000)
		    );
		  };
		    
        $scope.data = {
    		availableYear: [
		      {id: 2015, name: '2015'},
		      {id: 2016, name: '2016'},
		      {id: 2017, name: '2017'}
		    ],
		    availableMonth: [
		      {id: 1, name: 'January'},
		      {id: 2, name: 'February'},
		      {id: 3, name: 'March'},
		      {id: 4, name: 'April'},
		      {id: 5, name: 'May'},
		      {id: 6, name: 'June'},
		      {id: 7, name: 'July'},
		      {id: 8, name: 'August'},
		      {id: 9, name: 'September'},
		      {id: 10, name: 'October'},
		      {id: 11, name: 'November'},
		      {id: 12, name: 'December'}
		    ],
		    availableDay: [
		      {id: 1, name: '1'},
		      {id: 2, name: '2'},
		      {id: 3, name: '3'},
		      {id: 4, name: '4'},
		      {id: 5, name: '5'},
		      {id: 6, name: '6'},
		      {id: 7, name: '7'},
		      {id: 8, name: '8'},
		      {id: 9, name: '9'},
		      {id: 10, name: '10'},
		      {id: 11, name: '11'},
		      {id: 12, name: '12'},
		      {id: 13, name: '13'},
		      {id: 14, name: '14'},
		      {id: 15, name: '15'},
		      {id: 16, name: '16'},
		      {id: 17, name: '17'},
		      {id: 18, name: '18'},
		      {id: 19, name: '19'},
		      {id: 20, name: '20'},
		      {id: 21, name: '21'},
		      {id: 22, name: '22'},
		      {id: 23, name: '23'},
		      {id: 24, name: '24'},
		      {id: 25, name: '25'},
		      {id: 26, name: '26'},
		      {id: 27, name: '27'},
		      {id: 28, name: '28'},
		      {id: 29, name: '29'},
		      {id: 30, name: '30'},
		      {id: 31, name: '31'},
		    ],
		    weekdays: [
		      {id: 0, name: 'Sun'},
		      {id: 1, name: 'Mon'},
		      {id: 2, name: 'Tue'},
		      {id: 3, name: 'Wed'},
		      {id: 4, name: 'Thu'},
		      {id: 5, name: 'Fri'},
		      {id: 6, name: 'Sat'}
		    ],
   		};
   		
   		init_form();
    	$scope.getStatus();
    }
]);