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
                    
                    var name = scope.current.name + 
                            ' S' + pad(scope.current.season_number, 2) + 
                            'E' + pad(scope.current.episode_number, 2);
                    
                    $('#episode_name').text(name);
                    
                    var url = "http://" + window.location.host + "/content" + escape(scope.current.url);
                    
                    // create player
                    wjs("#player_wrapper").addPlayer({ id: "webchimera", theme: "sleek", autoplay: 1, buffer: 0, debug:true });

                    // add video url with an external subtitle
                    myplaylist = [];

                    myplaylist.push({
                            url: url,
                            subtitles: {
                                    "English": url.replace(".mkv", ".en.srt")
                            }
                    });

                    // add the playlist to the player
                    wjs("#webchimera").addPlaylist(myplaylist);
                });
            }
        };
    },
    
    pad = function (str, max) {
        str = str.toString();
        return str.length < max ? pad("0" + str, max) : str;
    }
        
    );