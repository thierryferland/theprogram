var services = angular.module('epicprog.services', []);

services.service('fileUpload', ['$http', '$state', '$mdDialog',
function($http, $mdDialog) {

	this.uploadFileToUrl = function(file, uploadUrl, user_email, successHandler, progressHandler, errorHandler) {
		var xhr = new XMLHttpRequest();
		var fd = new FormData();
		fd.append('file', file);
		fd.append('email', user_email);

		xhr.open('POST', uploadUrl);

		xhr.upload.onload = function() {
			successHandler();
		};

		xhr.upload.onprogress = function(e) {
			progressHandler(e);
		};

		xhr.upload.onerror = function(e) {
			errorHandler(e);
		};

		xhr.send(fd);

		// return $http.post(uploadUrl, fd, {
		// transformRequest: angular.identity,
		// headers: {'Content-Type': undefined}
		// });
	};
}]);

services.service('fileDownload', ['$http',
function($http) {
	this.downloadFile = function(dowloadUrl) {
		//var fd = new FormData();
		//d.append('file', file);
		$http.get(dowloadUrl, {
			//transformRequest: angular.identity,
			headers : {
				'Content-Type' : undefined
			}
		}).then(function(response) {
			console.log('success');
			var webmBlob = new Blob(response.data);
			//url = window.URL.createObjectURL(webmBlob);
		}, function(response) {
			// called asynchronously if an error occurs
			// or server returns response with an error status.
		});
		//return url;
	};
}]);

services.factory('epicApiRequest', ['$http',
function($http, $rootScope) {

	var service = {};

	function toPath(method, name) {

		path = method.replace('.', '/').replace(/(?:^|\.?)([A-Z])/g, function(x, y) {
			return "_" + y.toLowerCase();
		}).replace(/^_/, "");

		return path;
	}


	service.executeAuth = function(name, api_method, params, method) {
		if (window.location.hostname == 'localhost') {
			BASE_URL = window.location.origin + '/_ah/api';
		} else {
			BASE_URL = 'https://theprogramtracker.appspot.com/_ah/api';
		}

		base_url = BASE_URL;
		base_url += '/balance/v1';
		path = toPath(api_method, name);
		url = base_url + '/' + path;
		return http = $http({
			url : url,
			method : method,
			params : params
		});
	};

	return service;
}]); 