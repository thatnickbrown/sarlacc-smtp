#!/usr/bin/env bash

PITFILE=/pit.raw
PITDIR=/pit
PITSIZE="1G"
PITBIN="bin"
PITSMTP="smtp"

echo "This will create a loopback partition mounted as $PITDIR"
echo "backed by a $PITSIZE file $PITFILE. It will then deploy"
echo "sarlacc-smtp.py to this directory at set it to be executable"
echo "by the current user, $SUDO_USER."

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
    chmod 700 "$PITDIR"
fi

if mountpoint -q "$PITDIR"; then
    echo "$PITDIR is alrady mounted. Skipping mounting."
else
    echo "Mounting $PITFILE as $PITDIR."
    mount -t ext4 -o loop "$PITFILE" "$PITDIR"
fi

if [ -d "$PITDIR/$PITBIN" ]; then
    echo "$PITDIR/$PITBIN already exists. Skipping creation."
else
    echo "Creating binary directory for the pit: $PITDIR/$PITBIN"
    mkdir "$PITDIR/$PITBIN"
    chmod 700 "$PITDIR/$PITBIN"
fi

if [ -d "$PITDIR/$PITSMTP" ]; then
    echo "$PITDIR/$PITSMTP already exists. Skipping creation."
else
    echo "Creating SMTP activity directory for the pit: $PITDIR/$PITSMTP"
    mkdir "$PITDIR/$PITSMTP"
    chmod 600 "$PITDIR/$PITSMTP"
fi

if grep -q "$PITFILE" /etc/fstab; then
    echo "$PITFILE is already in fstab. Skipping automount setup."
else
    echo "Configuring fstab to automout $PITFILE as $PITDIR."
    echo "$PITFILE $PITDIR ext4 loop" >> /etc/fstab
fi

if [ -d "$PITDIR/$PITBIN/sarlacc-smtpd.py" ]; then
    echo "sarlacc-smtp.py is already in $PITDIR/$PITBIN. Skipping installation."
else
    echo "Copying sarlac-smtp to $PITDIR/$PITBIN."
    cp "sarlacc-smtp.py" "$PITDIR/$PITBIN"
    chmod 700 "$PITDIR/$PITBIN/sarlacc-smtp.py"
    echo "Setting /pit/ ownership to the current user."
    chown -R $SUDO_USER $PITDIR
    echo "You can run sarlacc-smtp with $PITDIR/$PITBIN/sarlacc-smtp.py ."
    echo "SMTP activity will be logged to $PITDIR/$PITSMTP."
fi

