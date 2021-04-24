#!/bin/bash
##########
# check if stream is live and start recording using youtube-dl
##########

full_path=$(dirname "$(realpath $0)")

source $full_path/config_list.sh



#check if not running, kill if running and stream is finished (broken record)
# [ -f $storage_path/$1/pid ] && $full_path/lifeChk.py $1 && exit 0 || kill -9 $(cat $storage_path/$1/pid)

#if pid exists and stream is live, than exit and do not start recording
[ -f $storage_path/$1/pid ] && $full_path/lifeChk.py $1 $twitchid && exit 0

echo $$ > $storage_path/$1/pid

#exit if no stream and remove lock
$full_path/lifeChk.py $1 $twitchid || rm $storage_path/$1/pid || exit 0

#set pid and start recording
/home/losted/.local/bin/youtube-dl -v -o $storage_path/$1/"%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s" twitch.tv/$1 >> $storage_path/$1/youtube-dl.log 2>&1 

# remove pid
rm $storage_path/$1/pid
