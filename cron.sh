#!/bin/bash
##########
# (actually main) script which cron (systemd.timer) starts by time
##########
full_path=$(dirname "$(realpath $0)")
source /opt/downloader/config_list.sh

for i in $list; do
    echo "$i is live?..."

    #check folder
    [ ! -d $storage_path/$i ] && mkdir -p $storage_path/$i && echo "Created dir $storage_path/$i"

    #detached check & start
    screen -dmS $i bash $full_path/check.sh $i
    sleep 2
    
done

#Show status
echo "===="

for i in $list; do
        [ -f $storage_path/$i/pid] && echo $i "is recording!" || echo $i "is not recording"
done
echo "===="
