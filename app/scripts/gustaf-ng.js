/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

angular.module('gustafApp', ['gustafFilters'])
    .controller('gustafController', function($scope, $http, $filter) {
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
        
        // Player 
        $scope.showModal = false;
        $scope.current = null;
        $scope.toggleModal = function(episode_id){
            
            $scope.showModal = !$scope.showModal;
            
            if ($scope.showModal === true) {
                $scope.current = $filter('filter')($scope.episodes, {id: episode_id}, true)[0];
                $('.modal').modal('show');
            } 
        };
    })

    .directive('gustafPlayer', function () {
        return {
            templateUrl: 'app/templates/gustaf-player.html',
            restrict: 'E',
            controller: function($scope, $element){
            },
            link: function(scope, element, attributes) {
                
                $(element).on('shown.bs.modal', function(e){
                    scope.vlc = document.getElementById('vlc');
                    if (scope.vlc)
                    {
                        var id = scope.vlc.playlist.add("content" + escape(scope.current.url));
                        scope.vlc.playlist.playItem(id);
                    }
                });
            }
        };
    });