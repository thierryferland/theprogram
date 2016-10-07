var controller = angular.module('epicprog.controller.account', []);
	

controller.controller('epicprog.controller.account', ['$scope', 'epicApiRequest', '$state','$rootScope',
    function accountCtl($scope, epicApiRequest, $state, $rootScope) {
    	
		 function subscribe() {  
		  // Disable the button so it can't be changed while  
		  // we process the permission request
		  //$scope.data.cb1_disabled = true;
		
		  navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {  
		    serviceWorkerRegistration.pushManager.subscribe({userVisibleOnly: true})  
		      .then(function(subscription) {  
		        // The subscription was successful  
		        isPushEnabled = true;
		        $scope.data.cb1_disabled = false;
		        //$scope.data.cb1 = true;
		
		        // Send the subscription.endpoint to your server  
		        // and save it to send a push message at a later date
		        return sendSubscriptionToServer(subscription, true);  
		      })  
		      .catch(function(e) {  
		        if (Notification.permission === 'denied') {  
		          // The user denied the notification permission which  
		          // means we failed to subscribe and the user will need  
		          // to manually change the notification permission to  
		          // subscribe to push messages
		          
		          message = 'Permission for Notifications was denied';
		          console.warn(message); 
		          $scope.message = message;
		          $scope.data.cb1_disabled = true;
		          $scope.data.cb1 = false;
		          
		        } else {  
		          // A problem occurred with the subscription; common reasons  
		          // include network errors, and lacking gcm_sender_id and/or  
		          // gcm_user_visible_only in the manifest.
		          $scope.data.cb1_disabled = true;
		          $scope.data.cb1 = false;
		          message = 'Unable to subscribe to push.';
		          console.error(message, e);  
		          console.warn(message); 
		          $scope.message = message;  
		        }  
		      });  
		  });  
		};
		
		function unsubscribe() {  
		  //$scope.data.cb1_disabled = true;
		
		  navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {  
		    // To unsubscribe from push messaging, you need get the  
		    // subscription object, which you can call unsubscribe() on.  
		    serviceWorkerRegistration.pushManager.getSubscription().then(  
		      function(pushSubscription) {  
		        // Check we have a subscription to unsubscribe  
		        if (!pushSubscription) {  
		          // No subscription object, so set the state  
		          // to allow the user to subscribe to push  
		          isPushEnabled = false;  
		          $scope.data.cb1_disabled = false;
		          //$scope.data.cb1 = false;
		          //pushButton.textContent = 'Enable Push Messages';  
		          return;  
		        }  
		
		        var subscriptionId = pushSubscription.subscriptionId;  
		        // Make a request to your server to remove  
		        // the subscriptionId from your data store so you
		        // don't attempt to send them push messages anymore
		        sendSubscriptionToServer(pushSubscription, false);  
		
		        // We have a subscription, so call unsubscribe on it  
		        pushSubscription.unsubscribe().then(function(successful) {  
		          $scope.data.cb1_disabled = false;
		          //$scope.data.cb1 = false;
		          //pushButton.textContent = 'Enable Push Messages';  
		          isPushEnabled = false;  
		        }).catch(function(e) {  
		          // We failed to unsubscribe, this can lead to  
		          // an unusual state, so may be best to remove
		          // the users data from your data store and
		          // inform the user that you have done so
		
		          console.log('Unsubscription error: ', e);  
		          $scope.data.cb1_disabled = false;
		          //$scope.data.cb1 = false;
		          //pushButton.textContent = 'Enable Push Messages';
		        });  
		      }).catch(function(e) {  
		        console.error('Error thrown while unsubscribing from push messaging.', e);  
		      });  
		  });  
		}
		
		 $scope.change_subscription = function() {
		 	if ($scope.data.cb1) {
		 		subscribe();
		 	}
		 	else {
		 		unsubscribe();
		 	}
		 };
    	
    	// Once the service worker is registered set the initial state  
		function initialiseState() {  
		  // Are Notifications supported in the service worker?  
		  if (!('showNotification' in ServiceWorkerRegistration.prototype)) {  
		  	var message = 'Notifications aren\'t supported.';
		    console.warn(message);
			$scope.message = message;
		    return;  
		  }
		
		  // Check the current Notification permission.  
		  // If its denied, it's a permanent block until the  
		  // user changes the permission  
		  if (Notification.permission === 'denied') {  
		    console.warn('The user has blocked notifications.');  
		    return;  
		  }
		
		  // Check if push messaging is supported  
		  if (!('PushManager' in window)) {
		  	var message = 'Push messaging isn\'t supported.';
		    console.warn(message);
		    $scope.message = message;
		    return;  
		  }
		
		  // We need the service worker registration to check for a subscription  
		  navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {  
		    // Do we already have a push message subscription?  
		    serviceWorkerRegistration.pushManager.getSubscription()  
		      .then(function(subscription) {  
		        // Enable any UI which subscribes / unsubscribes from  
		        // push messages.
		         $scope.data.cb1_disabled = false;
		        if (!subscription) {  
		          // We aren't subscribed to push, so set UI  
		          // to allow the user to enable push  
		          $scope.data.cb1 = false;
		          return;
		        }
		
		        // Keep your server in sync with the latest subscriptionId
		        $scope.data.cb1 = true;
		        sendSubscriptionToServer(subscription, true);
		
		        // Set your UI to show they have subscribed for  
		        // push messages  
		        //pushButton.selectedIndex = "1";
		        isPushEnabled = true;  
		      })  
		      .catch(function(err) {
		      	var message = 'Error during getSubscription()';
		        console.warn(message, err);
		        $scope.message = message;
		      });  
		  });  
		}
		    	
    	
    	function service_worker() {
			
		  // Check that service workers are supported, if so, progressively  
		  // enhance and add push messaging support, otherwise continue without it.  
			if ('serviceWorker' in navigator) {  
				navigator.serviceWorker.register('/service-worker.js') 
			 	.then(initialiseState);  
			  } else {  
			  	var message = 'Service workers aren\'t supported in this browser.';
			    console.warn(message);
			    $scope.message = message;
				}
		};
		    	
		// send subscription id to server
    	function sendSubscriptionToServer(subscription, yes_no) {
        	console.log(subscription);
        	params = {
    			'endpoint' : subscription.endpoint,
    			'is_subscribed' : yes_no
    		};
        	epicApiRequest.executeAuth('balance','user.subscription', params, 'POST').then(function(resp) {
    			if (!resp.code) {
    				$scope.is_subscribed = resp.data.is_subscribed;
    				console.log("subscription updated");
    			}
    		});
    	};
    	
    	// send subscription id to server
    	function getUserInfo() {
    		params = {};
        	epicApiRequest.executeAuth('balance','user.get', params, 'GET').then(function(resp) {
    			if (!resp.code) {
    				$scope.user = resp.data;
    			}
    		});
    		
    		
    		
    	};
    	
    	$scope.putUser = function() {
    		params = {'user.username' : $scope.user.username,'user.email' : $scope.user.email};
        	epicApiRequest.executeAuth('balance','user.put', params, 'POST').then(function(resp) {
    			if (!resp.code) {
    				console.log("user updated");
    			}
    		});    		
    	};
		    	
		var isPushEnabled = false;
		
		$scope.data = {
		    cb1: true,
		    cb1_disabled : false,
		  };
		    	
    	service_worker();
    	getUserInfo();
    	

    }
]);