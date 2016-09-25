from datetime import datetime

from channels.message import Message
from ..models import Room


def user_join(message, **kwargs):  # type: (Message, dict)
    """
    Handles a user joining a room
    :param message: The websocket message
    :param kwargs: Route kwargs
    :return:
    """
    room = Room.objects.get(slug=message.content.pop('slug'))
    username = message.content.pop('username')
    room.add_member(
        username=username,
        reply_channel_name=message.content.pop('reply_channel_name')
    )
    room.emit(
        event='user-join',
        data={
            'members': room.members(),
            'username': username,
            'youtube_id': room.youtube_id,
            'state': room.state,
            'action_time': str(room.action_time),
            'timestamp': room.timestamp
        }
    )


def user_leave(message, **kwargs):  # type: (Message, dict)
    """
    Handles when a user leaves the room
    """
    room = Room.objects.get(slug=message.content.pop('slug'))
    left_member = room.remove_member(reply_channel_name=message.reply_channel.name)

    # Send the user_leave message to the members in the room
    room.emit(
        event='user-leave',
        data={
            'members': room.members(),
            'username': left_member.username
        })
def state_change(message, **kwargs):
    """
    Handles when a user changes the state
    """
    room = Room.objects.get(slug=message.content.pop('slug'))
    username = message.content.pop('username')
    timestamp = message.content.pop('timestamp')
    state = message.content.pop('state')

    room.state = state
    room.timestamp = timestamp
    room.action_time = datetime.now()
    room.youtube_id = message.content.pop('youtube_id')
    room.save()

    room.emit(
        event='state-change',
        data={
            'state': room.state,
            'username': username,
            'action_time': str(room.action_time),
            'timestamp': room.timestamp,
            'youtube_id': room.youtube_id
        }
    )


def video_end(message, **kwargs):
    room = Room.objects.get(slug=message.content.pop('slug'))
    ended_video_id = message.content.pop('youtube_id')

    if room.youtube_id == ended_video_id:
        new_video_id = room.pop_video()
        room.youtube_id = new_video_id
        room.timestamp = 0
        room.action_time = datetime.now()
        room.state = 'play'
        room.save()

    room.emit(
        event='queue-next',
        data={
            'new_video_id': room.youtube_id,
            'timestamp': room.timestamp,
            'action_time': room.action_time,
            'state': room.state
        }
    )


def force_update(message, **kwargs):
    room = Room.objects.get(slug=message.content.pop('slug'))
    room.emit(
        event='force-update',
        data={
            'youtube_id': room.youtube_id,
            'timestamp': room.timestamp,
            'action_time': room.action_time,
            'state': room.state
        }
    )


def client_send(message, **kwargs):  # type: (Message, dict)
    """
    Handles when the client sends a message
    """
    room = Room.objects.get(slug=message.content.pop('slug'))

    # Send the new message to the room
    room.emit(
        event='message-new',
        data={
            'msg': message.content['msg'],
            'username': message.content['username'],
            'time': datetime.now().strftime('%I:%M:%S %p')
        })

