/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

var app = angular.module('sidebar-app', []);
app.controller('sidebar-controller', function($scope, $http) {
    $http.get("/shows").success(
        function(response) {
            $scope.shows = response;
        }
    );
});