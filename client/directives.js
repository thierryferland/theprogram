var directives = angular.module('epicprog.directives', []);

directives.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

directives.directive('histogram', ['epicApiRequest', function (epicApiRequest) {
    function link(scope, element, attrs) {
    	
    	function drawHisto(data) {
	    	var ctx = element[0].getContext('2d');
			var canvas, ctx;
			var max_drinks = 12;
			var drink_count = 0;
			var drink_height = 20;
			var day_width = 30;
			var buffer = 10;
			var zero_drink_buffer = 2;
			var limit = 4;
			
			drinks = data.drinks;
			
			// GOOD PRACTICE : SAVE CONTEXT AND RESTORE IT AT THE END
	        ctx.save();
	        // set the global context values
	        ctx.lineWidth=5;
	        
	        var hist_height = max_drinks * drink_height;

	        // font for all text drawing
	        ctx.font = 'italic 20pt Calibri';
	      
	        for (i = 0; i < drinks.length; i++) {
	          var day_left = (buffer + day_width) * i + buffer;
	          
	          var day_top = (max_drinks - drinks[i])*drink_height;
	          var day_height = hist_height - day_top + zero_drink_buffer;
	          
	          var grd_limit_top = (max_drinks - Math.min(limit,max_drinks))*drink_height;
	          var grd_limit_pct = grd_limit_top/(hist_height);

	          // Draw the two filled red rectangles
	          grd_drunk = ctx.createLinearGradient(day_left, 0, day_left, hist_height);
	          grd_drunk.addColorStop(0.1, "#E91E63");
	          grd_drunk.addColorStop(grd_limit_pct, "#FFEB3B");
	          grd_drunk.addColorStop(1, "#76FF03");
	          
	          ctx.fillStyle = grd_drunk;
	          
	          ctx.fillRect(day_left, day_top, day_width, day_height);
	          drink_count = drink_count + drinks[i];
	        }
	          // Draw a message above the rectangles
	          ctx.fillStyle = "#E91E63";
	          ctx.fillText(drink_count, 130, 30);
	          // GOOD PRACTICE !
	          ctx.restore();
        };
        
        params={email: scope.userStatus.user.username};
        epicApiRequest.executeAuth('balance','pot.getHistoryByDay', params, 'GET').then(function(resp) {
    							if (!resp.code) {
    								scope.limits = resp.data.limits;
    								scope.drinks = resp.data.drinks;
    								scope.lastseven = resp.data;
    								drawHisto(resp.data);
    							}
    						});
    };
    return {
    	link: link
  	};
}]); 

directives.directive('imgdemo', function () {
    return function (scope, element, attrs) {
        element.css('border', '5px solid');
        element.css('display', 'block');
        element.css('margin-left', 'auto');
        element.css('margin-right', 'auto');
    };
});

directives.directive('cursor', function () {
    return function (scope, element, attrs) {
        element.css('cursor', 'pointer');
    };
});

directives.directive('transparent', function () {
    return function (scope, element, attrs) {
        element.css('opacity', '0.92');
    };
});

directives.directive('bold', function () {
    return function (scope, element, attrs) {
        element.css('font-weight', '800');
    };
});

directives.directive('backbeer', function () {
    return function (scope, element, attrs) {
    	var today = new Date();
    	var image_number = today.getHours() % 4;
    	var img_url = 'url(images/background' + String(image_number) + '.jpg)';
        element.css('background', img_url);
        element.css('background-size', 'cover');
        element.css('background-repeat', 'no-repeat');
    };
});

directives.directive('epSignin', function() {
  return {
    controller: 'epicprog.controller.signinbutton',
    templateUrl: 'templates/signin.html'
  };
});

directives.directive('epUserCard', function() {
  return {
    controller: 'epicprog.controller.usercards',
    templateUrl: 'templates/usercards.html'
  };
});