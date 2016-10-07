var controller = angular.module('epicprog.controller.shame', []);
	

controller.controller('epicprog.controller.shame', ['$scope', 'epicApiRequest', '$state','fileUpload','fileDownload', '$mdDialog',
    function shameCtl($scope, epicApiRequest, $state, fileUpload, fileDownload, $mdDialog) {

		function get_videos() {
			params={};
			epicApiRequest.executeAuth('balance','getVideoUrls', params, 'GET')
			.then(function(resp) {
				if (!resp.code) {
					$scope.urls = resp.data.urls;
				}
			});
		};
	
		$scope.uploadFile = function() {
			
			getUploadURL = function() {
				params={};
	    		epicApiRequest.executeAuth('balance','getUploadUrl', params, 'GET').then(function(resp) {
	    							if (!resp.code) {
	    								var upload_url = resp.data.url;
	    								var user_email = resp.data.email;    								
	    								var file = $scope.myFile;
	    								
	    						        console.log('file is ' );
	    						        console.dir(file);
	    						        fileUpload.uploadFileToUrl(file, upload_url, user_email, 
	    						        	function() {
	    						        		$mdDialog.show(
											      $mdDialog.alert()
											        .clickOutsideToClose(true)
											        .textContent("Your video of shame was uploaded succesfully")
											        .ok('OK')
											        //.targetEvent(ev)
										    	);
										    	$scope.$apply(function() {
										    		get_videos();
										    	});
										    },
										    function(e) {
										    	$scope.$apply(function() {
										    		$scope.progress = e.loaded / e.total * 100;
										    	});							    	
										    },
										    function(){
									        	$mdDialog.show(
											      $mdDialog.alert()
											        .clickOutsideToClose(true)
											        .textContent("Something went wrong")
											        .ok('OK')
											        //.targetEvent(ev)
											    );
									        }									    
										);

	    							}
	    						});
	    	};
			
			$mdDialog.show(
		      $mdDialog.alert()
		        .clickOutsideToClose(true)
		        .textContent("Your video of shame is being uploaded")
		        .ok('Thanks!')
		        //.targetEvent(ev)
		    );

	    	getUploadURL();
	    	
	        
	    };    

		get_videos();
	}
]);