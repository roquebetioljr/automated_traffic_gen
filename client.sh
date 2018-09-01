#!/usr/bin/env bash

if [ $# != 6 ]; then
    echo "Correct usage. $ iperf_client.sh <path/to/store/results> <wireless interface> <server address> <port> <data rate> <test number>"
    exit 1
fi

if [ ! -d $1 ]; then
   mkdir $1
fi

cd $1

tcpdump -i $2 udp port $4 -vvv -ttt -c 19500 -w tcpdump_$6.pcap &
iperf -c $3 -b $5 -i 1 -f l -p $4 > iperf_$6.log

#sleep 1

#killall tcpdump
#killall iperf

exit 0