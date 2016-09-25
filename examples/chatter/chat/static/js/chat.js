// YOUTUBE ///


// 2. This code loads the IFrame Player API code asynchronously.
      var tag = document.createElement('script');

      tag.src = "https://www.youtube.com/iframe_api";
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      // 3. This function creates an <iframe> (and YouTube player)
      //    after the API code downloads.
      var player;
      function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
          height: '390',
          width: '640',
          videoId: 'M7lc1UVf-VE',
          events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
          }
        });
      }

      // 4. The API will call this function when the video player is ready.
      function onPlayerReady(event) {
        //event.target.playVideo();
      }

      // 5. The API calls this function when the player's state changes.
      //    The function indicates that when playing a video (state=1),
      //    the player should play for six seconds and then stop.
      var done = false;
      function onPlayerStateChange(event) {
        if (event.data == YT.PlayerState.PLAYING && !done) {
          done = true;
        }
      }
      function stopVideo() {
        player.stopVideo();
      }

      function updateCurrentTime() {
          $('#time').text(player.getCurrentTime());
      }

// WEB SOCKETS //

$(document).ready(function () {
    var room_slug = $('#room-slug').val();
    // Get the web socket path from the room slug
    var ws_path = '/chat/' + room_slug + '/stream/';
    // Create a new Channel instance (which handles connecting to server)
    var channel = new Channel(ws_path);

    channel.on('connect', function (channel) {
        /* var username = null;
        while (!username) {
            username = prompt('What is your username? (Required)');
        }

        var username_element = $('#chat-username');
        username_element.val(username);
        username_element.attr('disabled', true);

        channel.emit('user-join', {
            'username': username,
            'slug': room_slug,
        }) */
    });

    /**
     * Updates the member count in the chat room
     * @param data The data dictionary from the server
     */
    var handle_user_join = function (data) {

        // Set the video
        var youtube_id = data["youtube_id"];
        // The action time in milliseconds AGO
        var action_time = new Date() - new Date(data["action_time"]);
        var timestamp = parseFloat(data["timestamp"]);

        var starttime = timestamp + (action_time/1000);

        player.loadVideoById(youtube_id, starttime, "small");

        // Update members
        var members = data['members'];
        update_members(members);
    };

    var handle_user_leave = function (data) {
        update_members(data['members']);
    };

    var update_members = function (members) {
        var html = '';
        $.each(members, function (idx, member) {
            html += '<li class="list-group-item">';
            html += member['username'];
            html += '</li>';
        });
        $('#chat-members').html(html);
        $('#chat-member-count').html(members.length);
    };

    // Register the user-join and user-leave events
    channel.on('user-join', handle_user_join);
    channel.on('user-leave', handle_user_leave);


    var handle_state_change = function (data) {
        var new_state = data['state'];
        var timestamp = data['timestamp'];
        var acting_user = data['username'];
    };


    channel.on('state-change', handle_state_change);


    var binder = new Channel('/binding/');
    var bindingAgent = binder.bind('room');
    bindingAgent.create(function (data) {
        var roomItem =
            '<li data-room_id="'
            + data.pk
            + '" class="list-group-item">'
            + data.slug
            + '</li>';
        $("#chat-rooms").append(roomItem);
    });
    bindingAgent.update(function (data) {
        $("[data-room_id=" + data.pk + "]").html(data.slug);
    });
    bindingAgent.destroy(function (data) {
        $("[data-room_id=" + data.pk + "]").remove();
    });


      setInterval(updateCurrentTime, 100);


    $('#play').on('click', function (event) {
       player.playVideo();
    });

    $('#pause').on('click',function(event) {
        player.pauseVideo();
    });





    // MESSAGES //
    // Handle receiving new messages from other users
    channel.on('message-new', function (data) {
        $('#chat-messages').prepend(
            '<li class="list-group-item"><strong>'
            + data['username']
            + ":"
            + '</strong>&nbsp;'
            + data['msg']
            + '<span class="tag tag-pill tag-success float-right italics">'
            + data['time']
            + '</span></li>');
    });

    // Handle the user submitting new messages
    var submit_button = $('#chat-submit');
    submit_button.on('click', function () {
        // Get the username and message
        var username = $('#chat-username');
        var message = $('#chat-form');

        var data = {
            'msg': message.val(),
            'username': username.val()
        };

        // Don't let the user change his/her username
        username.attr('disabled', true);
        // Clear the message
        message.val('');

        // Send the message across the channel
        channel.emit('message-send', data);

        return false;
    });
});
