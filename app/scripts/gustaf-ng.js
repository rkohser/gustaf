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
        
        var NOT_WATCHED = [1, "Not watched", "danger"];
        var WATCHING = [2, "Watching", "warning"];
        var WATCHED = [3, "Watched", "success"];
        
        var TWO_MINUTES = 120; 
        
        $scope.toggleState = function(episode_id, episode_state) {
            var current = $filter('filter')($scope.episodes, {id: episode_id}, true)[0];
            if (episode_state[0] === 2 || episode_state[0] === 1) {
                // Watching or Not Watched -> Watched
                current.episode_state = WATCHED;
            } else {
                // Watched -> Not Watched
                current.episode_state = NOT_WATCHED;
            }
            
            $scope.updateState({
                id: episode_id,
                episode_state: current.episode_state
            });
        };
        
        $scope.updateProgress = function(episode_id, current_time_s, total_time_s) {
            
            var new_episode_state;
            if(current_time_s < TWO_MINUTES) {
                new_episode_state = NOT_WATCHED;
            } else if((total_time_s - current_time_s) < TWO_MINUTES) {
                new_episode_state = WATCHED;                
            } else {
                new_episode_state = WATCHING;
            }
            
            $scope.updateState({
                id: episode_id,
                episode_state: new_episode_state,
                current_time: current_time_s,
                total_time: total_time_s
            });
        };
        
        $scope.updateState = function(data){
            $http.put("/update", data);
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
            link: function($scope, element, attributes) {
                    
                // create player
                wjs("#player_wrapper").addPlayer({
                    id: "webchimera",
                    theme: "sleek",
                    autoplay: 1,
                    buffer: 0,
                    debug:true
                });
                
                $scope.wjs = wjs("#webchimera");
                    
                $(element).on('shown.bs.modal', function(e){

                    var name = $scope.current.name +
                            ' S' + pad($scope.current.season_number, 2) +
                            'E' + pad($scope.current.episode_number, 2);

                    $('#episode_name').text(name);

                    var url = "http://" + window.location.host + "/content" + escape($scope.current.url);
                    
                    var subtitles = {};
                    angular.forEach($scope.current.subtitles, function(lang){
                       subtitles[lang] = url.replace(".mkv", "." + lang + ".srt"); 
                    });

                    // add video url with an external subtitle
                    myplaylist = [];
                    myplaylist.push({
                            url: url,
                            subtitles: subtitles
                    });

                    // add the playlist to the player
                    $scope.wjs.addPlaylist(myplaylist);
                    
                    // create player
                    $scope.wjs.startPlayer();
                });
                
                $(element).on('hide.bs.modal', function(e){
                    
                    $scope.updateProgress($scope.current.id, $scope.wjs.time() / 1000.0, $scope.wjs.length() / 1000.0);
                    
                    $scope.wjs.stopPlayer();
                    $scope.wjs.clearPlaylist();
                    
                    $scope.showModal = !$scope.showModal;
                });
            }
        };
    },

    pad = function (str, max) {
        str = str.toString();
        return str.length < max ? pad("0" + str, max) : str;
    }

    );
