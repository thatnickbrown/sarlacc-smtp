# sarlacc-smtp
honeypot server that consumes every SMTP message

## requirements
```bash
pip3 install -r requirements.txt
```

## basic usage
```bash
./sarlacc-smtp.py -p 10025
```
```
creating email server controller
starting email server controller
sarlacc-smtp is listening on port 10025
```
You can then connect to it and send email messages:
```bash
$ telnet localhost 10025
```
```
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
220 email server Python SMTP 1.4.4.post2
helo spelling matters
250 email server
mail from: anyone
250 OK
rcpt to: anywhere
250 OK
data
354 End data with <CR><LF>.<CR><LF>
this isn't even formed correctly
.
250 Message will be devoured
quit
221 Bye
Connection closed by foreign host.
```
Messages will be saved to disk using the current time in nanoseconds as filenames.

## installation and configuration
The easiest way to kick it off and walk away would be:
```bash
$ nohup ./sarlacc-smtp.py &
```
If you want sarlacc-smtp to survive reboots you can use systemd. This example runs on port 25 as root from the directory /pit/:
```bash
$ sudo cat /etc/systemd/system/sarlacc-smtp.service
```
```
[Unit]
Description=sarlacc-smtp
After=network.target

[Service]
WorkingDirectory=/pit
ExecStart=/pit/sarlacc-smtp.py -p 25

[Install]
WantedBy=multi-user.target
```
```bash
$ sudo systemctl start sarlacc-smtp.service
$ sudo systemctl enable sarlacc-smtp.service
```
### security considerations
It is advisable to run sarlacc-smtp (or any other honeypot) from a sandboxed environment.
#### running it on port 25 as a user
Since regular users cannot bind low ports, using [nft redirect](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_\(NAT\)) can can bypass this restriction.
#### limiting disk usage
Because sarlacc consumes everything, it is advisable to limit how much disk space is available to it.
The included script, ```dig-sarlacc-pit.sh```, will create a 1GB file ```/pit.raw``` and mount it as ```/pit```. You can run sarlacc-smtp from this directory to ensure the rest of the system is unaffected if more than 1GB of data is collected.
```bash
sudo ./dig-sarlacc-pit.sh
cp sarlacc-smtp.py /pit
/pit/sarlacc-smtp.py
```
There are many ways to do this:
- use use a dedicated partition or LVM partition
- use btrfs quota to set a directory size limit
- use xfs project to set a directory size limit
- run it in docker and specify the flag ```--storage-opt size=1G```
- use the linux quota system