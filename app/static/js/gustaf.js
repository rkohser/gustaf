var gustaf = {}

$(function(){

    // Init page
    $('#progress').hide();

    // Init web sockets
    gustaf.show_ws = new WebSocket("ws://localhost:8888/show");
    gustaf.play_ws = new WebSocket("ws://localhost:8888/play")

    // Show web socket
    gustaf.show_ws.onmessage = function(evt) {
        $('#episodes').html(evt.data);
    };

    // Play web socket
    gustaf.play_ws.onmessage = function(evt) {
        var msg = JSON.parse(evt.data)
        switch(msg.state) {
            case "playing":
                $('#status').text("VLC playing " + msg.file)
                $('#progress').show();
                $('#progress').attr("style", "width: " + msg.progress + "%");
                $('#progress').attr("aria-valuenow", msg.progress);
                $('#progress').addClass("active");
                break;
            case "paused":
                $('#status').text("VLC paused " + msg.file)
                $('#progress').removeClass("active");
                break;
            case "stopped":
                $('#status').text("VLC not playing")
                $('#progress').hide();
                break;
        }
    }

    gustaf.getEpisodesForSeason = function(seasonId) {
        gustaf.show_ws.send(seasonId);
    };

    gustaf.play = function(episode_id) {
        gustaf.play_ws.send(episode_id)
    }
})