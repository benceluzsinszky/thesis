#!/bin/bash

LOG_FILE="$HOME/resource_logger.log"

while true; do
    DATE=$(date '+%Y-%m-%d %H:%M:%S')

    # Get CPU usage
    CPU_IDLE=$(mpstat 1 1 | awk '/Average/ {print $NF}')
    CPU_USAGE=$(echo "100 - $CPU_IDLE" | bc)

    # Get RAM usage
    RAM_USAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')

    # Get Received network traffic
    RX_BYTES=$(cat /sys/class/net/eth0/statistics/rx_bytes)
    # Get Transmitted network traffic
    TX_BYTES=$(cat /sys/class/net/eth0/statistics/tx_bytes)
    # Average network traffic over 100ms
    sleep 0.1
    RX_BYTES_NEW=$(cat /sys/class/net/eth0/statistics/rx_bytes)
    TX_BYTES_NEW=$(cat /sys/class/net/eth0/statistics/tx_bytes)
    RX_RATE=$(echo "scale=2; ($RX_BYTES_NEW - $RX_BYTES) * 10 / 1024" | bc)
    TX_RATE=$(echo "scale=2; ($TX_BYTES_NEW - $TX_BYTES) * 10 / 1024" | bc)

    echo "$DATE CPU: ${CPU_USAGE}%, RAM: $RAM_USAGE, RX: ${RX_RATE}KB/s, TX: ${TX_RATE}KB/s"
    echo "$DATE CPU: ${CPU_USAGE}%, RAM: $RAM_USAGE, RX: ${RX_RATE}KB/s, TX: ${TX_RATE}KB/s" >> $LOG_FILE

    sleep 0.1
done