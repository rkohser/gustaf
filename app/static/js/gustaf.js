var gustaf = {};

$(document).ready(function () {

    var spin_opts = {
        lines: 8, // The number of lines to draw
        length: 3, // The length of each line
        width: 5, // The line thickness
        radius: 9, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 8, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#000', // #rgb or #rrggbb or array of colors
        speed: 0.9, // Rounds per second
        trail: 63, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    };

    // Init page
    $('#progress').hide();

    // Build WebSocket URL
    var buildWSUrl = function (wsName) {
        return "ws://" + window.location.host + "/" + wsName;
    };

    // Init web sockets
    gustaf.show_ws = new WebSocket(buildWSUrl("show"));
    gustaf.play_ws = new WebSocket(buildWSUrl("play"));

    // Show web socket
    gustaf.show_ws.onmessage = function(evt) {
        var msgList = JSON.parse(evt.data);
        var nMsg = msgList.length;
        for (var i = 0; i < nMsg; i++) {
            var msg = msgList[i];
            switch (msg.message_type) {
            case "load_show":
                // Display episode list
                $('#episodes').html(msg.data);
                break;
            case "update_episode_state":
                setEpisodeState(msg.episode_id, msg.state, msg.current_time, msg.total_time, msg.play_state);
                break;
            case "update_season_state":
                setSeasonState(msg.season_id, msg.state);
                break;
            case "update_show_state":
                setShowState(msg.show_id, msg.state);
                break;
            case "get_subtitles":
                setSubtitleState(msg.episode_id, msg.lang, msg.result);
                break;
            case "update_episode_progress":
                setEpisodeProgress(msg.episode_id, msg.current_time, msg.total_time, msg.play_state);
            };
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
    gustaf.getEpisodesForShow = function(showId, showName) {
        var message = {};
        message.action = "load_show";
        message.show_id = showId;
        message.show_name = showName;
        gustaf.show_ws.send(JSON.stringify(message));
    };

    // to play the given episode
    gustaf.play = function(episode_id) {
        var message = {};
        message.action = "play_episode";
        message.episode_id = episode_id;
        gustaf.play_ws.send(JSON.stringify(message));
    };

    // to get subtitles for the given episode
    gustaf.get_subtitles = function(episode_id, lang) {
        var message = {};
        message.action = "get_subtitles";
        message.episode_id = episode_id;
        message.lang = lang
        gustaf.show_ws.send(JSON.stringify(message));

        $("#sub_episode_" + episode_id + "_" + lang).spin(spin_opts)
            .css("position","relative");
    };

    // to manage the play state
    gustaf.toggleEpisodeState = function(object, episode_id) {
        var message = {};
        message.action = "update_episode_state";
        message.episode_id = episode_id;
        gustaf.show_ws.send(JSON.stringify(message));
    };

    gustaf.toggleSeasonState = function(object, season_id) {
        var message = {};
        message.action = "update_season_state";
        message.season_id = season_id;
        message.state = object.text();
        gustaf.show_ws.send(JSON.stringify(message));
    };

    var setEpisodeState = function(episode_id, stateArray, current_time, total_time, play_state) {

        //full progress bar if not playing
        var progress = 100;
        if (stateArray[1] == "Watching") {
            progress = current_time / total_time * 100;
        };

        var progress_elt = $("#progress_episode_" + episode_id);

        //update progress
        progress_elt.attr("style", "width: " + progress + "%")
            .attr("aria-valuenow", progress)
            .removeClass()
            .addClass("progress-bar progress-bar-" + stateArray[2]);

        //update text
        $("#progress_episode_" + episode_id + " > span")
            .text(stateArray[1]);

        //active stripes
        if (play_state == "playing") {
            progress_elt.addClass("progress-bar-striped")
            .addClass("active");
        } else {
            progress_elt.removeClass("active")
                .removeClass("progress-bar-striped");
        };
    };

    var setSeasonState = function(season_id, stateArray) {
        // select element with id
        $("#state_season_" + season_id)
            .removeClass()
            .addClass("label label-" + stateArray[2])
            .text(stateArray[1]);
    };

    var setShowState = function(show_id, stateArray) {
        // select element with id
        $("#state_show_" + show_id)
            .removeClass()
            .addClass("btn btn-" + stateArray[2]);
    };

    var setSubtitleState = function(episode_id, language, result) {
        $("#sub_episode_" + episode_id + "_" + language)
            .spin(false)
            .removeClass()
            .addClass("btn btn-" + result);
    };
});
