/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

var app = angular.module('gustafFilters', [])
    .filter('progress', function() {
        return function(episode) {
            var total = episode.total_time;
            var current = episode.current_time;
            var state = episode.episode_state[0];
            
            if (state === 2) {
                // Watching
                return current / total * 100.0;
            } else {
                return 100.0;
            }
        };
    });