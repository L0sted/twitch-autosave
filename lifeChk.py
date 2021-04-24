#!/usr/bin/python3
#################
# return 0 if streamer is live (continue execution while in bash), 1 if not
#################
import sys
if (not sys.argv[1]) or (not sys.argv[2]):
       sys.exit(2)

from twitch import TwitchClient

client = TwitchClient(client_id=sys.argv[2]) #client init
user_id=client.users.translate_usernames_to_ids(sys.argv[1])[0].id #get id
#get live by id (if var not empty)

if client.streams.get_stream_by_user(user_id):
    print(user_id)
    print(client.streams.get_stream_by_user(user_id).stream_type)
    if client.streams.get_stream_by_user(user_id).stream_type == 'live':
        sys.exit(0)

sys.exit(1)
