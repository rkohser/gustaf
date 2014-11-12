var gustaf = {}

$(function(){

    gustaf.ws = new WebSocket("ws://localhost:8888/websocket");
    gustaf.ws.onopen = function() {
    };
    gustaf.ws.onmessage = function (evt) {
       $('#episodes').html(evt.data);
    };

    gustaf.getEpisodesForSeason = function(seasonId) {

        gustaf.ws.send(seasonId);

    };

})