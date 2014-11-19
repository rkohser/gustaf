var gustaf = {}

$(function(){

    gustaf.show_ws = new WebSocket("ws://localhost:8888/show");
    gustaf.play_ws = new WebSocket("ws://localhost:8888/play")

    gustaf.show_ws.onmessage = function(evt) {
        $('#episodes').html(evt.data);
    };

    gustaf.play_ws.onmessage = function(evt) {
        $('#progress').attr("style", "width: " + evt.data + "%");
    }

    gustaf.getEpisodesForSeason = function(seasonId) {
        gustaf.show_ws.send(seasonId);
    };

    gustaf.play = function(episode_id) {
        gustaf.play_ws.send(episode_id)
    }
})