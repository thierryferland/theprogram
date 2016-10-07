var router = angular.module('epicprog.router', [ 'satellizer']);

router
	.config(
		function($locationProvider) {
			$locationProvider.html5Mode({
			  enabled: true,
			  requireBase: false
			});
		});

router
    .config(
        function($urlRouterProvider) {

            $urlRouterProvider.otherwise("/demo");

        });

router
    .config(
        function($stateProvider, $authProvider) {

            $stateProvider

                .state('login', {
                    url :'/login',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.login',
                            templateUrl: 'templates/login.html',
                        },
                    },
                })
                
                .state('signup', {
                    url :'/signup',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.signup',
                            templateUrl: 'templates/signup.html',
                        },
                    },
                })
                
                .state('setup', {
                    url :'/setup',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.setup',
                            templateUrl: 'templates/setup.html',
                        },
                    },
                    resolve: {
			          loginRequired: loginRequired
			        }
                })
                
                .state('welcome', {
                    url :'/welcome',
                    views :  {
                        '': {
                            templateUrl: 'templates/welcome.html',
                        },
                    },
                })

                .state('add', {
                    url :'/',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.add',
                            templateUrl: 'templates/add.html',
                        },
                    },
                    resolve: {
			          loginRequired: loginRequired
			        }
                })

                .state('edit', {
                    url :'/edit/{id}',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.edit',
                            templateUrl: 'templates/rules.html',
                        },
                    },
                })
                
                .state('account', {
                    url :'/account',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.account',
                            templateUrl: 'templates/account.html',
                        },
                    },
                    resolve: {
			          loginRequired: loginRequired
			        }
                })
                
                .state('rules', {
                    url :'/rules',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.rules',
                            templateUrl: 'templates/rules.html',
                        },
                    }
                })
                
                .state('shame', {
                    url :'/shame',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.shame',
                            templateUrl: 'templates/shame.html',
                        },
                    },
                    resolve: {
			          loginRequired: loginRequired
			        }
                })
                
                .state('histo', {
                    url :'/histo',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.histo',
                            templateUrl: 'templates/histo.html',
                        },
                    },
                })

                .state('demo', {
                    url :'/demo',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.demo',
                            templateUrl: 'templates/demo.html',
                        },
                    },
                })
                
                .state('email', {
                    url :'/email?year=&month=&day=&nDrinks=',
                    views :  {
                        '': {
                            controller: 'epicprog.controller.email',
                            templateUrl: 'templates/email.html',
                        },
                    },
                    resolve: {
			          loginRequired: loginRequired
			        }
                });
                
		    function skipIfLoggedIn($q, $auth) {
		      var deferred = $q.defer();
		      if ($auth.isAuthenticated()) {
		        deferred.reject();
		      } else {
		        deferred.resolve();
		      }
		      return deferred.promise;
		    }
		
		    function loginRequired($q, $location, $auth, $rootScope, $state) {
		      var deferred = $q.defer();
		      if ($auth.isAuthenticated()) {
		      	$rootScope.islogin = true;
		        deferred.resolve();
		      } else {
		        $location.path('/');
		        //$state.go('welcome');
		      }
		      return deferred.promise;
		    }

    });