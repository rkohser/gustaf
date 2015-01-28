﻿var gustaf = {};

$(document).ready(function(){

    // Init page
    $('#progress').hide();

    // Init web sockets
    gustaf.show_ws = new WebSocket("ws://localhost:8888/show");
    gustaf.play_ws = new WebSocket("ws://localhost:8888/play");

    // Show web socket
    gustaf.show_ws.onmessage = function(evt) {
        var msg = JSON.parse(evt.data);
        switch (msg.action) {
            case "load_season":
                // Display episode list
                $('#episodes').html(msg.data);
                break;
        };        
    };

    // Play web socket
    gustaf.play_ws.onmessage = function(evt) {
        var msg = JSON.parse(evt.data);
        switch (msg.state) {
        case "playing":
            $('#status').text("VLC playing " + msg.file);
            $('#progress').show();
            $('#progress').attr("style", "width: " + msg.progress + "%");
            $('#progress').attr("aria-valuenow", msg.progress);
            $('#progress').addClass("active");
            break;
        case "paused":
            $('#status').text("VLC paused " + msg.file);
            $('#progress').removeClass("active");
            break;
        case "stopped":
            $('#status').text("VLC not playing");
            $('#progress').hide();
            break;
        };
    };

    // to request the episode list
    gustaf.getEpisodesForSeason = function(seasonId) {
        var message = {};
        message.action = "load_season";
        message.season_id = seasonId;
        gustaf.show_ws.send(JSON.stringify(message));
    };

    // to play the given episode
    gustaf.play = function(episode_id) {
        gustaf.play_ws.send(episode_id);
    };

    // to manage the play state
    gustaf.toggleState = function(object, episode_id) {
        object
    };
});