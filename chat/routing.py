from channels import route, route_class
from .consumers import ChatServer, events, Demultiplexer, RoomBinding

chat_routing = [
    route_class(ChatServer, path=r'^(?P<slug>[^/]+)/stream/$'),
]

event_routing = [
    route('chat.receive', events.user_join, event=r'^user-join$'),
    route('chat.receive', events.user_leave, event=r'^user-leave$'),
    route('chat.receive', events.state_change, event=r'^state-change$'),
    route('chat.receive', events.client_send, event=r'^message-send$'),

    route('chat.receive', events.video_end, event=r'^video-end$'),
    route('chat.receive', events.force_update, event=r'^force-update$'),
]

binding_routing = [
    route_class(Demultiplexer, path=r'^/binding/'),
    route('binding.room', RoomBinding.consumer),
]
