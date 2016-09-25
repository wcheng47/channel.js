import json

from channels import Group
from django.db import models


class Room(models.Model):
    """
    Represents a room containing chat users
    """
    # The name of the room found in the room URL
    slug = models.CharField(max_length=32, unique=True)
    # URL code of the video
    youtube_id = models.CharField(max_length=32, null = True)
    # Play or pause state
    state = models.CharField(max_length=8, null = True)
    # What  time in history the state changes
    action_time = models.DateTimeField(null = True)
    # the  timestamp when the state changes
    timestamp = models.FloatField(null = True)

    SEPARATOR = ','

    video_queue = models.TextField(default='')

    @property
    def videos(self):
        return self.video_queue.split(Room.SEPARATOR)
    
    def pop_video(self):
        return_id = self.poll_video()

        self.video_queue = Room.SEPARATOR.join(self.videos[1:])
        self.save()

        return return_id
    
    def poll_video(self):
        return self.videos[0]

    def push_video(self, new_video_id): # type: str
        self.video_queue += Room.SEPARATOR + new_video_id
        self.save()

    def emit(self, event, data):  # type: (str, dict)
        data['event'] = event
        self.group.send({
            'text': json.dumps(data)
        })

    def add_member(self, **kwargs):  # type: (dict) -> Member
        """
        Adds a new member to this room
        :param kwargs: The properties of the new user
        :return: The new member
        """
        kwargs['room'] = self
        new_member = Member.objects.create(**kwargs)
        self.member_set.add(new_member)
        return new_member

    def remove_member(self, **kwargs):  # type: (dict) -> Member
        """
        Removes a members from this room
        :param kwargs: The search parameters for finding the Member to remove
        :return: The removed Member
        """
        member = self.member_set.get(**kwargs)
        member.delete()
        return member

    def members(self):  # type: () -> [dict]
        """
        Returns an array of member information
        """
        return [member.as_dict for member in self.member_set.all()]

    @property
    def member_count(self):    # type: () -> int
        return self.member_set.count()

    @property
    def group(self):  # type: () -> Group
        return Group(self.slug)

    def __str__(self):
        return "'{}' room ({} members)".format(self.slug, self.member_count)


class Member(models.Model):
    """
    Represents a user that belongs to a room
    """
    room = models.ForeignKey(Room, null=False)
    username = models.CharField(max_length=128, null=False)
    # The name of the reply_channel
    reply_channel_name = models.CharField(max_length=128, null=False)

    @property
    def as_dict(self):  # type: () -> dict
        """
        Provides a serialized version of this member
        :return:
        """
        return {
            'username': self.username
        }
