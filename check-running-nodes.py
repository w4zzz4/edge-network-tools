import json
import smtplib, ssl
from datetime import datetime
from urllib.request import urlopen

# URL of the statistics
url = "https://stargate.edge.network/sessions/open"

# List of edge hosts
# The device "name" can be found with the command : sudo edge device info
# Column[0] = Edge Device
# Column[1] = Friendly Name
# Column[2] = Start date of the edge device
# Column[3] = Last activity of the edge device
xe_hosts = [
    ("xe_1234567890000000000000000000000000000000", "Friendly Name 1","-","-"),
    ("xe_1234567890000000000000000000000000000001", "Friendly Name 2","-","-"),
    ("xe_1234567890000000000000000000000000000002", "Friendly Name 3","-","-"),
]
  
# Get the statistics and store the JSON
response = urlopen(url)
data_json = json.loads(response.read())

#Parse the JSON and update the List of edge hosts with Start & LastActive field
for i in range(len(xe_hosts)):
    for j in range(len(data_json)):
        if data_json[j]["node"]["address"] == xe_hosts[i][0]:
            xe_hosts[i] = (xe_hosts[i][0],
                             xe_hosts[i][1], 
                             str(datetime.fromtimestamp(float(str(data_json[j]["start"])[0:10])))[0:16],
                             str(datetime.fromtimestamp(float(str(data_json[j]["lastActive"])[0:10])))[0:16]
                          )

#Send an email with the status of all edge hosts contained in xe_hosts
sender_email = "email@office365.com"
receiver_email = "email@office365.com"
message = """\
Subject: Edge Network : Status

| Start                         | Last                         | Host
---------------------------------------------------------------------------------
"""
for i in range(len(xe_hosts)):
    message = message + "| " + str(xe_hosts[i][2]) +  " | " + str(xe_hosts[i][3]) + " | " + xe_hosts[i][1] + "\r\n"

smtp_server = "smtp.office365.com"
port = 587  # For starttls
sender_email = "email@office365.com"
password = "password"

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
try:
    server = smtplib.SMTP(smtp_server,port)
    server.ehlo() # Can be omitted
    server.starttls(context=context) # Secure the connection
    server.ehlo() # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit() 