# sarlacc-smtp
honeypot server that consumes every SMTP message

## requirements
```bash
pip3 install -r requirements.txt
```

## basic use
```
./sarlacc-smtp.py -p 10025
creating email server controller
starting email server controller
sarlacc-smtp is listening on port 10025
```
You can then connect to it and send email messages:
```
nc -C localhost 10025
220 workgroup.local email server
helo spelling.is.important.su
250 workgroup.local
mail from: trustme@phishers.su
250 OK
rcpt to: whoever
250 OK
data
354 End data with <CR><LF>.<CR><LF>
This doesn't even include a subject! yeesh.
.
250 Message will be devoured
quit
221 Bye
```
SMTP messages and other SMTP data collected by sarlacc-smtp will be saved to ./smtp/.

## installation and configuration
The easiest way to kick it off and walk away would be:
```bash
nohup /pit/bin/sarlacc-smtp.py &
```
If you want sarlacc-smtp to survive reboots you can use systemd. This example runs on port 25 as root from the directory /pit/:
```bash
sudo cat /etc/systemd/system/sarlacc-smtp.service
```
```
[Unit]
Description=sarlacc-smtp
After=network.target

[Service]
WorkingDirectory=/pit
ExecStart=/pit/bin/sarlacc-smtp.py -p 25

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl start sarlacc-smtp.service
sudo systemctl enable sarlacc-smtp.service
```
### security considerations
It is advisable to run sarlacc-smtp (or any other honeypot) from a sandboxed environment.
#### running it on port 25 as a user
Since regular users cannot bind low ports, using [nft redirect](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_\(NAT\)) can can bypass this restriction.
#### limiting disk usage
Because sarlacc consumes everything, it is advisable to limit how much disk space is available to it. The included installation script, ```dig-sarlacc-pit.sh``` (run using sudo), will create a 1GB file ```/pit.raw``` and mount it as ```/pit``` and deploy sarlacc-smtp.py to this loopback partition. You can run sarlacc-smtp from within /pit to ensure the rest of the system is unaffected if more than 1GB of data is collected.

There are many ways to do this:
- use use a dedicated partition or LVM partition
- use btrfs quota to set a directory size limit
- use xfs project to set a directory size limit
- run it in docker and specify the flag ```--storage-opt size=1G```
- use the linux quota system