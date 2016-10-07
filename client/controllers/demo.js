var controller = angular.module('epicprog.controller.demo', []);

controller.controller('epicprog.controller.demo', ['$scope','epicApiRequest', '$state',
    function demoCtl($scope, epicApiRequest, $state) {

        function request_user()
        {
            epicApiRequest.executeAuth('balance', 'user.request', {}, 'POST')
                .then(function (resp) {
                if (!resp.code) {
                    var money_popup = document.querySelector('#popupDone');
                    money_popup.innerHTML = "User was requested, we'll contact you.";
                    money_popup.showModal();
                    setTimeout(function () {
                        money_popup.close()
                    }, 3000);
                }
                })
                .catch(function (resp) {
                    var money_popup = document.querySelector('#popupDone');
                    money_popup.innerHTML = "User request failed. Please try again later.";
                    money_popup.showModal();
                    setTimeout(function () {
                        money_popup.close()
                    }, 3000);
                });
        }
    }
]);