help_full = Enter a query to search for a track.
    If the track is not found, try entering a more accurate query.
    The search is performed in the music.youtube.com database (and only there).
    Inline mode is available. Type @{$botname} *<track>* in any chat.
    An option to subscribe to a performer is available. Upon subscription, the bot will automatically send new releases to the chat.
    Some commands can be entered both with arguments and on their own.
    To learn more about how commands work, type: /{$helpcommand} *<command>*
    Recommendations are available! Just send the bot your favorite track and get a list tailored for you! (*Important*: the track must be forwarded from this bot, otherwise the result will be unpredictable)

help_start =  *{$com}*: basic command to start the bot. If the bot was blocked, restarting it unfreezes subscriptions.
    Manual call is not necessary

help_help = What is not clear?

help_force = *{$com}*: command for direct downloading of a track via a link from music.youtube.com.
    Example: /{$com} {"https://music.youtube.com/watch?v=YCi7qXeA\\_vM"}.
    It is also acceptable to type the command and send the link separately.
    Convenient if the track is already playing in YouTube Music or for some reason cannot be found through the bot's interface.
    {"*Important!*"}: tracks are downloaded only from the music.youtube.com resource. Other links will be rejected.

help_playlist = *{$com}*: command for downloading a playlist via a link. Similar to the /{$comForce} command, but for playlists. You can also type the command and send the link separately.
    Example: /{$com} {"music.youtube.com/playlist?list=OLAK5uy\\_kodfrWJRKHZNTPRTIx8NWqcvYhNeZnqnA"}

help_unsubscribe = *{$com}*: removes a subscription to a performer. You can also type the command and send the performer separately.
    Example: /{$com} instasasalka

help_subscribe = *{$com}*: allows you to subscribe to a performer. You can also type the command and send the performer separately.
    Every few days, the bot checks the performers' releases and sends new ones to the chat when they appear.
    Example: /{$com} {"[OXVGEN](https://music.youtube.com/@oxvgen9)"}

help_subscriptions = *{$com}*: shows all your subscriptions. Can be used as a standalone command.
    Example: /{$com} arc (will show all subscriptions that include the word {"*arc*"})

help_albums = *{$com}*: allows you to get all albums of the specified artist.
    Example: /{$com} Currents (will show all albums released by {"*Currents*"})

help_catalog = *{$com}*: allows you to get all albums of the specified artist.
    Example: /{$com} thrown (will show all singles released by {"*thrown*"})

help_cancel = *{$com}*: cancels actions. Used where commands are entered in multiple steps

help_unknown_arg = Unknown argument: {$args}
