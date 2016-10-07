var controller = angular.module('epicprog.controller.setup', []);

controller.controller('epicprog.controller.setup', ['$scope', '$state', '$mdPanel',
function setupCtl($scope, $state, $mdPanel) {

	$scope.newProgram = function(e) {
		var position = $mdPanel.newPanelPosition().absolute().center();
		var animation = $mdPanel.newPanelAnimation();
		animation.openFrom('.animation-target');
		animation.closeTo('.animation-target');
		animation.withAnimation($mdPanel.animation.SCALE);
		var config = {
			animation : animation,
			attachTo : angular.element(document.body),
			//controller : DialogCtrl,
			controllerAs : 'ctrl',
			templateUrl : 'templates/program.html',
			panelClass : 'demo-dialog-example',
			position : position,
			zIndex : 150,
			//clickOutsideToClose : true,
			clickEscapeToClose : true,
		};
		$mdPanel.open(config);
	};
}]); 