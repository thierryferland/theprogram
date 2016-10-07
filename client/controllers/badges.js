var controller = angular.module('epicprog.controller.badges', []);
	

controller.controller('epicprog.controller.badges', ['$scope', '$state','badges',
    function badgesCtl($scope, $state, badges) {

    	$scope.user_badges = badges;
    	
    }
]);