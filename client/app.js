var app = angular.module('epicprog', [
	'ui.router',
    'epicprog.router',
    'epicprog.controller',
    'epicprog.directives',
    'epicprog.services',
    'ngMaterial',
    'satellizer'
]);

app.config(function($mdThemingProvider) {
  $mdThemingProvider.theme('default')
    .primaryPalette('pink')
    .accentPalette('light-green')
    .warnPalette('light-blue')
    .backgroundPalette('blue-grey');
});

app.config(function($authProvider, $rootScopeProvider) {
	$authProvider.google({
	  clientId: '510637458696-qj8hljf6eqc7fnv883bdd3jisso2almb.apps.googleusercontent.com'
	});
});

app.run(['$state', '$rootScope',
    function($state, $rootScope) {
		 
    }
]);