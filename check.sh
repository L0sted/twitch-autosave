#!/bin/bash
##########
# check if stream is live and start recording using youtube-dl
##########

source /opt/downloader/list.sh
#check if not running
[ -f $path/$1/pid ] && exit 0

#check if live
/opt/downloader/lifeChk.py $1 || exit 0


#set pid and start downloading
touch $path/$1/pid
/home/ubuntu/.local/bin/youtube-dl -v -o $path/$1/"%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s" twitch.tv/$1 >> $path/$1/youtube-dl.log
rm $path/$1/pid
