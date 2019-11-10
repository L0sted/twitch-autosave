#!/bin/bash
##########
# (actually main) script which cron (systemd.timer) starts by time
##########
source /opt/downloader/list.sh

for i in $list; do
    echo "$i is live?..."

    #check folder
    [ ! -d $path/$i ] && mkdir -p $path/$i && echo "Created dir $path/$i"

    #detached check & start
    screen -dmS $i bash /opt/downloader/check.sh $i
    sleep 5
    
done

#Show status
echo "===="

for i in $list; do
        cat $path/$i/pid 2>/dev/null && echo $i "is recording!" || echo $i "is not recording"
done
echo "===="
