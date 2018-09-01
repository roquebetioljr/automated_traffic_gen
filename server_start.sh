#!/usr/bin/env bash

if [ $# != 4 ]; then
    echo "Correct usage. $ iperf_client.sh <path/to/store/results> <wireless interface> <port> <test number>"
    exit 1
fi

if [ ! -d $1 ]; then
   mkdir $1
fi

cd $1

tcpdump -i $2 port $3 -vvv -ttt -c 19500 -w tcpdump_server_$3_$4.pcap &
iperf -s -u -i 1 -f k -p $3 > iperf_server_$3_$4.txt &

exit 0
