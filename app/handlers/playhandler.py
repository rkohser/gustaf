import tornado.websocket
import tornado.ioloop

from model import Episode
from core import VLCProcess, VLCState
from core import register_handler, get_handler
from core import PlayStateManager
from core import Message, MessageType, parse_message


class PlayHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.vlc = VLCProcess()
        self.vlc.register_end_callback(self.on_play_end)
        self.vlc.register_progress_callback(self.on_play_progress)
        self.episode_id = None
        self.episode_state = None
        self.last_current_time = None
        self.last_total_time = None
        self.last_status = None
        self.last_episode_state = None

    def initialize(self, name):
        register_handler(name, self)

    def open(self):
        print("Play webSocket opened")

    def on_message(self, message):
        """
        Handles message from the websocket
        :param message:
        :return:
        """
        msg = parse_message(message)
        if msg.message_type == MessageType.PLAY_EPISODE:
            if not self.episode_id:
                self.episode_id = msg.episode_id
                episode = Episode.get(id=msg.episode_id)
                self.last_episode_state = episode.episode_state
                self.vlc.play(episode.path, episode.current_time)
            else:
                print("Already playing, close first instance and retry")

    def on_close(self):
        print("Play webSocket closed")

    def on_play_end(self):
        msg_list = []
        if self.last_status:
            PlayStateManager.update_episode(self.episode_id, self.last_episode_state, self.last_episode_state,
                                            self.last_status.current_time, self.last_status.total_time)

            msg_list.append(Message(MessageType.UPDATE_EPISODE_STATE, episode_id=self.episode_id,
                                    state=self.last_episode_state,
                                    current_time=self.last_status.current_time,
                                    total_time=self.last_status.total_time,
                                    play_state=VLCState.STOPPED))

            get_handler('show').write_message(Message.to_json(msg_list))

        self.episode_id = None
        self.episode_state = None
        self.last_current_time = None
        self.last_total_time = None
        self.last_status = None
        self.last_episode_state = None

    def on_play_progress(self, status):

        msg_list = []
        if status.state == VLCState.PLAYING:
            episode_state = status.deduce_episode_state()
            old_episode_state = self.last_episode_state
            self.last_episode_state = episode_state

            if old_episode_state != episode_state:
                msg_list.extend(PlayStateManager.update_episode(self.episode_id, old_episode_state, episode_state,
                                                                status.current_time, status.total_time))

        # Play progress
        if msg_list:
            episode_message = msg_list[0]
            assert episode_message.message_type == MessageType.UPDATE_EPISODE_STATE
            episode_message.current_time = status.current_time
            episode_message.total_time = status.total_time
            episode_message.play_state = status.state
        else:
            msg_list.append(Message(MessageType.UPDATE_EPISODE_STATE, episode_id=self.episode_id,
                                    state=episode_state,
                                    current_time=status.current_time,
                                    total_time=status.total_time,
                                    play_state=status.state))

        get_handler('show').write_message(Message.to_json(msg_list))

        self.last_status = status
        # self.write_message(status.to_json())

    def write_message(self, message):
        """
        Sends a message to the websocket
        :param message:
        {
            "get_time": int seconds,
            "file": string,
            "get_length": int seconds,
            "state": "playing"|"stopped"|"paused",
            "progress": int percents
        }
        :return:
        """
        super().write_message(message)
