import os.path
import json
import smtplib, ssl
from datetime import datetime
from urllib.request import urlopen
from configparser import ConfigParser

###################
# Variables
###################
xe_wallets = []
xe_hosts = []
urlCS = "https://stargate.edge.network/sessions/open?fields=node.address,start,lastActive"
urlAva = "https://index.xe.network/session/"            # URL Availability
mErrors = ""

###################
# Config
###################
config = ConfigParser()
config.read('/home/username/scripts/edge-network.ini')

## Wallets
if config.has_section('WALLETS') == True:
    data = config.options('WALLETS')
    for var in data:
        xe_wallets.append(config.get('WALLETS', var))

## Hosts
if config.has_section('HOSTS') == True:
    data = config.options('HOSTS')
    for var in data:
        xe_hosts.append(config.get('HOSTS', var).split(','))

## Earnings
try:
    vEarnings = config['EARNINGS']
    ea_limite_url = vEarnings['limit_url']
    ea_limite_show = vEarnings['limit_show']
except Exception as e:
    print("Error in config section 'EARNINGS'")
    print("Value : " + str(e))
    exit()

## Email settings
try:
    vMail = config['EMAIL']
    mail_smtp_server = vMail['smtp_server']
    mail_smtp_port = vMail['smtp_port']
    mail_sender_email = vMail['sender_email']
    mail_receiver_email = vMail['receiver_email']
    mail_password = vMail['password']
except Exception as e:
    print("Error in config section 'MAIL'")
    print("Value : " + str(e))
    exit()

## Cleaning
del data
del vEarnings
del vMail

###################
# Working stuff
###################

## Create the title
mMessage = """\
Subject: Edge Network : Status

"""

## Status of the nodes
## Get the statistics and store the JSON
response = urlopen(urlCS)
data_json = json.loads(response.read())

## Parse the JSON and update the list of edge hosts with Start & LastActive
for i in range(len(xe_hosts)):
    for j in range(len(data_json)):
        if data_json[j]["node"]["address"] == xe_hosts[i][0]:
            xe_hosts[i] = (xe_hosts[i][0],
                             xe_hosts[i][1], 
                             str(datetime.fromtimestamp(float(str(data_json[j]["start"])[0:10])))[0:16],
                             str(datetime.fromtimestamp(float(str(data_json[j]["lastActive"])[0:10])))[0:16]
                          )

mMessage = mMessage + """\
| Start                         | Last                         | Host
----------------------------------------------------------------------------"""
for i in range(len(xe_hosts)):
    mMessage = mMessage  + "\r\n" + "| " + str(xe_hosts[i][2]) +  " | " + str(xe_hosts[i][3]) + " | " + xe_hosts[i][1]

## Number of running nodes in Edge Network
mMessage = mMessage + "\r\n\r\nYou have " + str(len(xe_hosts)) + " hosts on " + str(j) + " Edge Network nodes (" + str(len(xe_hosts)*100/j)[0:5] + "%)"

## Earnings information
mEarnings = ""
for i in range(len(xe_wallets)):
    response = urlopen("https://index.xe.network/transactions/" + xe_wallets[i] + "?limit=20&page=1&sort=-timestamp")
    data_json = json.loads(response.read())
    mMessage = mMessage + "\r\n"

    #Parse the JSON and store last earnings
    j=0
    for i in range(len(data_json["results"])):
        if str(data_json["results"][i]["data"]["memo"][0:13]) == "Node Earnings":
            j=j+1
            mMessage = mMessage + "\r\n" + str(datetime.fromtimestamp(float(str(data_json["results"][i]["timestamp"])[0:10])))[0:10] + " : " + str(data_json["results"][i]["amount"]/1000000) + " : " + str(data_json["results"][i]["data"]["memo"])
            if j >= 5:
                break

## Availability + Metrics
mMessage = mMessage + """\r\n\r\n\
  Avai | Host
---------------------------------"""

for i in range(len(xe_hosts)):
    try:
        response = urlopen(urlAva + xe_hosts[i][0])
        data_json = json.loads(response.read())
        if data_json["availability"] == 1:
            mMessage = mMessage + "\r\n" + str(data_json["availability"]*100)  + " % | "
            mMessage = mMessage + xe_hosts[i][1]
        else:
            mMessage = mMessage + "\r\n" + str(data_json["availability"]*100)[0:5]  + "  | "
            mMessage = mMessage + xe_hosts[i][1]
    except:
        mErrors = mErrors + "\r\nError in urlAva : " + urlAva + xe_hosts[i][0] + " | " + xe_hosts[i][1]
        print("Error in urlAva : " + urlAva + xe_hosts[i][0] + " | " + xe_hosts[i][1])

# Finalize message
mMessage = mMessage + "\r\n\r\n" + mErrors

###############
# Email setup #
###############
## Send Email
# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
try:
    server = smtplib.SMTP(mail_smtp_server,mail_smtp_port)
    server.ehlo() # Can be omitted
    server.starttls(context=context) # Secure the connection
    server.ehlo() # Can be omitted
    server.login(mail_sender_email, mail_password)
    server.sendmail(mail_sender_email, mail_receiver_email, mMessage)
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit() 

############
# Telegram #
############
#Uncomment the 2 lines below to activate the Telegram Message
#import telegram_send
#telegram_send.send(messages=[mMessage])