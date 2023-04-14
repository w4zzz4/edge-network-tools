# edge-network-tools
## edge-network-stats.py  
1. You need to adapt the line 21 to your location of the script and the .ini file  
> config.read('/home/username/scripts/edge-network.ini')
 
 2. You need to configure the Phyton Telegram component (still need to be documented)
 3. You need to uncomment 2 lines to activate Telegram Messsage, lines 160 & 161
> #import telegram_send  
> #telegram_send.send(messages=[mMessage])
 ## edge-network.ini
 1. Fill the wallet(s) to monitor for the earnings
 2. Fill the host(s) to monitor
 3. Configure the smtp server to send the mail
