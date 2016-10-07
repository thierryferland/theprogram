var controller = angular.module('epicprog.controller.email', []);

controller.controller('epicprog.controller.email', ['$scope', '$state', '$stateParams', '$mdDialog','epicApiRequest',
    function emailCtl($scope, $state, $stateParams, $mdDialog, epicApiRequest) {

		$scope.showAlert = function(ev,message) {
		    $mdDialog.show(
		      $mdDialog.alert()
		        .clickOutsideToClose(true)
		        .textContent(message)
		        .ok('Thanks!')
		        .targetEvent(ev)
		    );
		  };

    	$scope.addDrink = function() {
    		var message = "You drinks were entered for " + $stateParams.month + "/" + $stateParams.day;
    		params = {'date.year' : parseInt($stateParams.year),
				'date.month' : parseInt($stateParams.month),
				'date.day' : parseInt($stateParams.day),
				'nDrinks' : parseInt($stateParams.nDrinks)};
    		epicApiRequest.executeAuth('balance','drink.add', params, 'POST').then(function(resp) {
    			if (!resp.code) {
					$scope.showAlert(null, message);
    			}
    		});
    	};
    	
    	$scope.addDrink();
    	$state.go('add');

    }
]);