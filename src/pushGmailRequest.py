# -*- coding: utf-8 -*-
import os, sys, smtplib, getpass, datetime
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

user_name = #email
password = getpass.getpass('Enter your password: ')


now = datetime.datetime.now()
data_path = os.getcwd() + "/data/"
dir_path = data_path + str(now.year) + '_' + sys.argv[1] + "week"

target_name = []
people = pd.read_csv(data_path + "people.csv", encoding="utf-8")
cur_submitter = pd.read_csv(dir_path + "/cur_submitter.csv", encoding="utf-8")

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(user_name, password)
    
for i in range(len(cur_submitter)):
    if cur_submitter["제출"][i] == 0:
         target_name.append(people.ix[i]["이메일"])

print (target_name)
if target_name:
    msg = MIMEMultipart()
    msg['From'] = user_name
    msg['Subject'] = "[" + sys.argv[1] + " Weekly Report] You have not submitted your weekly research report yet"

    body = "Hi, I'm Report Manager\n\n\n You have not submitted your weekly research report yet. Please submit it as soon as possible."
    
    for i in range(len(target_name)):
        msg['To'] = target_name[i]
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        server.sendmail(user_name, target_name[i], text)
        print("\nENDED PUSH EMAIL TO " + target_name[i] + "!")
    
server.quit()

