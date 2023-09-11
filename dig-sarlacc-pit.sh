#!/usr/bin/env bash

PITFILE=/pit.raw
PITDIR=/pit
PITSIZE="1G"

if test -f "$PITFILE"; then
    echo "$PITFILE already exist. Skipping creation."
else
    echo "Creating $PITFILE."
    fallocate -l $PITSIZE $PITFILE
    echo "Formatting $PITFILE."
    mkfs.ext4 $PITFILE
fi

if [ -d "$PITDIR" ]; then
    echo "$PITDIR already exists. Skipping creation."
else
    mkdir "$PITDIR"
fi

if mountpoint -q "$PITDIR"; then
    echo "$PITDIR is alrady mounted. Skipping mounting."
else
    echo "Mounting $PITFILE as $PITDIR."
    mount -t ext4 -o loop "$PITFILE" "$PITDIR"
fi

if grep -q "$PITFILE" /etc/fstab; then
    echo "$PITFILE is already in fstab. Skipping automount setup."
else
    echo "Configuring fstab to automout $PITFILE as $PITDIR."
    echo "$PITFILE $PITDIR ext4 loop" >> /etc/fstab
fi

echo "Configuring $PITDIR to be readable and writeable by anyone."
echo "The pit devours everything (until it runs out of space.)"
chmod 777 "$PITDIR"
