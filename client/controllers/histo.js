var controller = angular.module('epicprog.controller.histo', []);
	

controller.controller('epicprog.controller.histo', ['$scope', '$state','userStatus',
    function statsCtl($scope, $state, userStatus) {

    	$scope.userStatus = userStatus;
    	
    }
]);