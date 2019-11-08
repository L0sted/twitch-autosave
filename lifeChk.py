#!/usr/bin/python3
#################
# return 0 if streamer is live (continue exec while in bash), 1 if not
#################
import sys
#if not sys.argv[1]:
#	sys.exit(2)

twitchid = "59hrsplx7dmvc17pqkqcm9l3n1uzc4"
from twitch import TwitchClient
client = TwitchClient(client_id=twitchid) #client init
user_id=client.users.translate_usernames_to_ids(sys.argv[1])[0].id #get id
#get live by id (if var not empty)

if client.streams.get_stream_by_user(user_id):
	sys.exit(0)
else:
	sys.exit(1)

