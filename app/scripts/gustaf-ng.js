/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

angular.module('gustafApp', ['gustafFilters'])
    .controller('gustafController', function($scope, $http) {
        $http.get("/shows").success(
            function(response) {
                $scope.shows = response;
            }
        );

        $scope.getEpisodesPerShowId = function(showId) {
            $http.get("/episodes/" + showId).success(
                function(response) {
                    $scope.episodes = response;
                });
        };
    });