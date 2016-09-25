from django.shortcuts import render
from django.http.response import HttpResponse
import json

from django.views.decorators.csrf import csrf_exempt


from .models import Room


def chatroom(request, slug):  # type: (HttpRequest, str) -> HttpResponse
    """
    Handles displaying the chat room page
    :param request: The HTTP request
    :param slug: The name of the room
    :return: The metronome room with the given name
    """
    room, created = Room.objects.get_or_create(slug=slug)
    rooms = Room.objects.all()
    return render(request=request,
                  template_name='chat/room.html',
                  context={
                      'room': room,
                      'rooms': rooms,
                  })

@csrf_exempt
def add_to_video_queue(request, slug):
    room = Room.objects.get(slug=slug)
    new_video_id = request.POST['new_video_id']
    rec_slug = request.POST['slug']

    if rec_slug != slug or new_video_id is None or len(new_video_id) < 8:
        raise ValueError()

    room.push_video(new_video_id)

    d = {
        'video_ids': room.videos,
    }

    return HttpResponse(json.dumps(d))
