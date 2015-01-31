var gustaf = {};

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
            case "load_show":
                // Display episode list
                $('#episodes').html(msg.data);
                break;
            case "update_episode_state":
                setEpisodeState(msg.episode_id, msg.state)
                break;
            case "update_season_state":
                setSeasonState(msg.season_id, msg.state)
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
    gustaf.getEpisodesForShow = function(showId) {
        var message = {};
        message.action = "load_show";
        message.show_id = showId;
        gustaf.show_ws.send(JSON.stringify(message));
    };

    // to play the given episode
    gustaf.play = function(episode_id) {
        gustaf.play_ws.send(episode_id);
    };

    // to manage the play state
    gustaf.toggleEpisodeState = function(object, episode_id) {
        var message = {};
        message.action = "update_episode_state";
        message.episode_id = episode_id;
        message.state = object.text();
        gustaf.show_ws.send(JSON.stringify(message));
    };

    gustaf.toggleSeasonState = function(object, season_id) {
        var message = {};
        message.action = "update_season_state";
        message.season_id = season_id;
        message.state = object.text();
        gustaf.show_ws.send(JSON.stringify(message));
    };

    setEpisodeState = function(episode_id, stateArray) {
        // select tr with id
        $("#state_episode_" + episode_id)
            .removeClass()
            .addClass("label label-" + stateArray[2])
            .text(stateArray[1]);
    };

    setSeasonState = function(season_id, stateArray) {
        // select tr with id
        $("#state_season_" + season_id)
            .removeClass()
            .addClass("label label-" + stateArray[2])
            .text(stateArray[1]);
    };
});