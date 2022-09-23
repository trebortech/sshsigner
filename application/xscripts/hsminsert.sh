#!/bin/bash

PORTFILE=/usr/local/bin/ports.conf
LISTENIP="127.0.0.1"
connector_path='/usr/bin/yubihsm-connector'

# If the ports file does not exist create with a default port range
[[ -f "$PORTFILE" ]] || echo "11111" >> $PORTFILE

# Grab the existing running yubihsm-connector processes
currprocess=$(ps -ef | grep 'yubihsm')
# Get a list of currently inserted YubiHSM
results=$(lsusb -d 1050:0030 -v 2>/dev/null | grep iSerial)

for OUTPUT in $results
do
        if [[ "$OUTPUT" =~ ^[0-9]{10}$ ]]; then
                # Remove leading 0 from serial number
                cleanserial=$(echo $OUTPUT | sed 's/^0*//')

                # Check if the service is already running for this serial number
                if [[ "$currprocess" =~ "$cleanserial" ]]; then
                    echo "Process already running $cleanserial"
                else
                    # Lookup up ports file for previous port
                    currvalue=$(awk -v var=$cleanserial '$1 ~ var {print}' < $PORTFILE)
                    if [ -z "$currvalue" ]; then
                        # Get next port number from line 1
                        useport=$(sed '1!d' < $PORTFILE)
                        # Increase next port number by 10
                        nextport=$((useport+10))
                        # Update the port file so the next port number is different
                        sed -i -r "1s/.*/$nextport/" $PORTFILE
                        echo "$cleanserial:$useport" >> $PORTFILE
                    else
                        useport=$(echo $currvalue | awk '{split($0,a,":"); print a[2]}')
                        # Startup with this port number
                    fi
                    # Start the process
                    ipport="$LISTENIP:$useport"
                    /usr/bin/nohup $connector_path --listen $ipport --serial $cleanserial &
                fi
        fi
done