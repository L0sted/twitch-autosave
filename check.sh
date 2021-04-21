#!/bin/bash
##########
# check if stream is live and start recording using youtube-dl
##########

full_path=$(dirname "$(realpath $0)")

source $full_path/config_list.sh



#check if not running, kill if running and stream is finished (broken record)
# [ -f $storage_path/$1/pid ] && $full_path/lifeChk.py $1 && exit 0 || kill -9 $(cat $storage_path/$1/pid)
[ -f $storage_path/$1/pid ] && $full_path/lifeChk.py $1 && exit 0

#exit if no stream
$full_path/lifeChk.py $1 || exit 0
echo `$full_path/lifeChk.py $1`

#set pid and start downloading

nohup /home/losted/.local/bin/youtube-dl -v -o $storage_path/$1/"%(upload_date)s_%(title)s__%(timestamp)s_%(id)s.%(ext)s" twitch.tv/$1 >> $storage_path/$1/youtube-dl.log 2>&1 & echo $! > $storage_path/$1/pid

#remove pid

rm $storage_path/$1/pid
