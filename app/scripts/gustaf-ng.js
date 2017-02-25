/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

angular.module('gustafApp', ['gustafFilters'])
    .controller('gustafController', function($scope, $http, $filter) {

        $scope.spinning = false;
        $scope.refresh = function(){
            $scope.spinning = true;
            $http.get("/refresh").success(
                function(response){
                    console.log(response);
                    $scope.spinning = false;
                    refreshDashboard();
                }
            );
        };

        // Shows
        $scope.currentShowName = null;
        $scope.refreshShows = function(){
            $http.get("/shows").success(
                function(response) {
                    $scope.shows = response;
                }
            );
        };

        var refreshDashboard = function () {
            $http.get("/added").success(
                function (response) {
                    $scope.addedEpisodes = response;
                }
            );

            $http.get("/next").success(
                function (response) {
                    $scope.nextEpisodes = response;
                }
            );

            $http.get("/started").success(
                function (response) {
                    $scope.startedEpisodes = response;
                }
            );
        };

        $scope.NUMBER_SORTING = ["season_number", "episode_number"];

        var resetDashboard = function () {
            $scope.addedEpisodes = null;
            $scope.nextEpisodes = null;
            $scope.startedEpisodes = null;
        };

        $scope.getEpisodes = function (showId, showName) {

            resetDashboard();

            $scope.currentShowName = showName;
            $http.get("/episodes/" + showId).success(
                function(response) {
                    $scope.episodes = response;
                });
        };
        
        $scope.NOT_WATCHED = [1, "Not watched", "danger"];
        $scope.WATCHING = [2, "Watching", "warning"];
        $scope.WATCHED = [3, "Watched", "success"];
        
        var TWO_MINUTES = 120; 
        
        $scope.toggleState = function(episode) {
            if (episode.episode_state[0] === $scope.WATCHING[0] || episode.episode_state[0] === $scope.NOT_WATCHED[0]) {
                // Watching or Not Watched -> Watched
                episode.episode_state = $scope.WATCHED;
            } else {
                // Watched -> Not Watched
                episode.episode_state = $scope.NOT_WATCHED;
            }
            
            $scope.updateState({
                id: episode.id,
                episode_state: episode.episode_state
            });
        };
        
        $scope.updateProgress = function(episode, current_time_s, total_time_s) {
            
            var new_episode_state;
            var new_current_time = 0;
            if(current_time_s < TWO_MINUTES) {
                new_episode_state = $scope.NOT_WATCHED;
            } else if((total_time_s - current_time_s) < TWO_MINUTES) {
                new_episode_state = $scope.WATCHED;                
            } else {
                new_episode_state = $scope.WATCHING;
                new_current_time = current_time_s;
            }
            
            episode.current_time = new_current_time;
            episode.total_time = total_time_s;
            episode.episode_state = new_episode_state;
            
            $scope.updateState({
                id: episode.id,
                episode_state: new_episode_state,
                current_time: new_current_time,
                total_time: total_time_s
            });
        };
        
        $scope.updateState = function(data){
            $http.put("/update", data);

            $scope.refreshShows();
        };

        // Player
        $scope.showModal = false;
        $scope.current = null;
        $scope.toggleModal = function(episode){

            $scope.showModal = !$scope.showModal;

            if ($scope.showModal === true) {
                $scope.current = episode;
                $('.modal').modal('show');
            }
        };

        // first load the shows
        $scope.refreshShows();

        // then load dashboard
        refreshDashboard();
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
                    autoplay: 0,
                    buffer: 0,
                    debug:true
                });
                
                $scope.wjs = wjs("#webchimera");
                    
                $(element).on('shown.bs.modal', function(e){

                    var url = "http://" + window.location.host + "/content" + escape($scope.current.url);
                    
                    var subtitles = {};
                    angular.forEach($scope.current.subtitles, function(lang){
                       subtitles[lang] = url.replace(".mkv", "." + lang + ".srt"); 
                    });

                    // add video url with an external subtitle
                    var myplaylist = [];
                    myplaylist.push({
                            url: url,
                            subtitles: subtitles
                    });

                    // add the playlist to the player
                    $scope.wjs.addPlaylist(myplaylist);
                    
                    // start watching
                    $scope.wjs.startPlayer();
                    
                    // go to current time
                    if($scope.current.episode_state[0] === $scope.WATCHING[0]) {
                        $scope.wjs.time($scope.current.current_time * 1000);
                    }
                    
                });
                
                $(element).on('hide.bs.modal', function(e){
                    
                    $scope.updateProgress($scope.current, $scope.wjs.time() / 1000.0, $scope.wjs.length() / 1000.0);
                    
                    $scope.wjs.stopPlayer();
                    $scope.wjs.clearPlaylist();
                    
                    $scope.showModal = !$scope.showModal;
                });
            }
        };
    })

    .directive('gustafEpisodes', function () {
        return {
            templateUrl: 'app/templates/gustaf-episodes.html',
            restrict: 'E',
            scope: {
                showName: '@',
                title: '@',
                episodes: '=',
                sortFields: '=',
                play: '&',
                toggleState: '&',
                getEpisodes: '&'
            }
        };
    });
