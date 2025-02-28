#!/bin/bash

LOG_FILE="resource_log.txt"
NET_INTERFACE="enp41s0"  # Change this based on your actual network interface

while true; do
    DATE=$(date +"%Y-%m-%d %H:%M:%S")

    # Get CPU usage per core 
    CPU_STATS=$(mpstat -P ALL 1 1 | awk 'NR>3 && $2 ~ /^[0-9]+|all$/ {printf "CPU %s: %.2f%%, ", $2, 100 - $12}')

    # Get RAM usage
    RAM_USAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')

    # Get Received network traffic
    if [ -e "/sys/class/net/enp41s0/statistics/rx_bytes" ]; then
        RX_BYTES=$(cat /sys/class/net/enp41s0/statistics/rx_bytes)
        TX_BYTES=$(cat /sys/class/net/enp41s0/statistics/tx_bytes)
        # Average network traffic over 100ms
        sleep 0.1
        RX_BYTES_NEW=$(cat /sys/class/net/enp41s0/statistics/rx_bytes)
        TX_BYTES_NEW=$(cat /sys/class/net/enp41s0/statistics/tx_bytes)
        RX_RATE=$(awk "BEGIN {print ($RX_BYTES_NEW - $RX_BYTES) * 10 / 1024}")
        TX_RATE=$(awk "BEGIN {print ($TX_BYTES_NEW - $TX_BYTES) * 10 / 1024}")
    else
        RX_RATE="N/A"
        TX_RATE="N/A"
    fi

    # Print CPU stats for all cores
    echo "$DATE CPU Usage per core:"
    echo "$CPU_STATS"
    echo "RAM: $RAM_USAGE, RX: ${RX_RATE}KB/s, TX: ${TX_RATE}KB/s"

    # Log everything to a file
    {
        echo "$DATE CPU Usage per core:"
        echo "$CPU_STATS"
        echo "RAM: $RAM_USAGE, RX: ${RX_RATE}KB/s, TX: ${TX_RATE}KB/s"
    } >> "$LOG_FILE"

    sleep 0.1
done