# -*- coding: utf-8 -*-
import email, hashlib, getpass, imaplib
import sys, os, re, math
from os.path import exists
from collections import defaultdict, Counter
import platform, datetime, base64
import pandas as pd

fileNameCounter = Counter()
fileNameHashes = defaultdict(set)
NewMsgIDs = set()
ProcessedMsgIDs = set()

def isNotInWeek(date, now):
    date_tuple = email.utils.parsedate_tz(date)
    if ((now.year != date_tuple[0]) or (now.month != date_tuple[1]) or (abs(now.day - date_tuple[2]) > 2)):
        return True
    else:
        return False

def isKorean(subject):
    return re.search(matchKorean, subject) is not None

def nameIndexing(msg, file_name):
    fn = file_name.split('.')[0]
    ext = file_name.split('.')[1]

    msg = msg['From'].split()
    index_name = people.loc[people['이름'] == UTFdecoder(msg[0])].index

    index_email = people.loc[people['이메일'] == re.search(matchEmail, msg[1]).group(0)].index

    if(len(index_name) is 1):
        idx = index_name.values[0]

    elif(len(index_email) is 1):
        idx = index_email.values[0]

    else:
        return file_name

    if(ext == 'pdf'):
        hashTable["제출"][idx] = 1
    
    return str(idx) + '.' + ext

def UTFdecoder(sender):
    if isKorean(sender):
        sender = sender.split("\r\n\t")
        decoded = ""
        for i in range(len(sender)):
            parsed_string = sender[i].split("?")
            decoded += base64.b64decode(parsed_string[3]).decode(parsed_string[1], "ignore")
        return decoded
    else:
        return sender

def recover(resume_file):
    if os.path.exists(resume_file):
        print('Recovery file found resuming...')
        with open(resume_file) as f:
            processed_ids = f.read()
            for ProcessedId in processed_ids.split(','):
                ProcessedMsgIDs.add(ProcessedId)
    else:
        print('No Recovery file found.')
        open(resume_file, 'a').close()


def GenerateMailMessages(gmail_user_name, p_word, resume_file):
    imap_session = imaplib.IMAP4_SSL('imap.gmail.com')

    typ, account_details = imap_session.login(gmail_user_name, p_word)

    print(typ)
    print(account_details)
    if typ != 'OK':
        print('Not able to sign in!')
        raise NameError('Not able to sign in!')
    imap_session.select('inbox')
    typ, data = imap_session.search(None, '(X-GM-RAW "has:attachment")')
    
    if typ != 'OK':
        print('Error searching Inbox.')
        raise NameError('Error searching Inbox.')
    
    for msgId in data[0].split()[::-1]:
        NewMsgIDs.add(msgId)
        typ, message_parts = imap_session.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            print('Error fetching mail.')
            raise NameError('Error fetching mail.')
        email_body = message_parts[0][1]
        if msgId not in ProcessedMsgIDs:
            yield email.message_from_bytes(email_body)
            ProcessedMsgIDs.add(msgId)
            with open(resume_file, "a") as resume:
                resume.write('{id},'.format(id=msgId))

    imap_session.close()
    imap_session.logout()


def save_attachments(msg, dir_path):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_name = UTFdecoder(part.get_filename())
        if file_name is not None:
            file_name = ''.join(file_name.splitlines())
        if file_name:
            payload = part.get_payload(decode=True)
            if payload:
                x_hash = hashlib.md5(payload).hexdigest()
                if x_hash in fileNameHashes[file_name]:
                    print('Skipping duplicate file: {file}'.format(file=file_name))
                    continue
                fileNameCounter[file_name] += 1
                file_str, file_extension = os.path.splitext(file_name)
                if fileNameCounter[file_name] > 1:
                    new_file_name = '{file}({suffix}){ext}'.format(suffix=fileNameCounter[file_name],
                                                                   file=file_str, ext=file_extension)
                    print('Renaming and storing: {file} to {new_file}'.format(file=file_name,
                                                                                new_file=new_file_name))
                else:
                    new_file_name = file_name
                name_index = nameIndexing(msg, new_file_name)
                fileNameHashes[file_name].add(x_hash)
                file_path = os.path.join(dir_path, name_index)
                
                if os.path.exists(file_path):
                    print('Existing file: {file}'.format(file=name_index))
                    continue

                with open(file_path, 'wb') as fp:
                    print('Storing: [{origin_file}] <===== {indexing_file}'.format(origin_file=name_index,indexing_file=new_file_name))
                    fp.write(payload)
                    
            else:
                print('Attachment {file} was returned as type: {ftype} skipping...'.format(file=file_name, ftype=type(payload)))
                continue
            

resumeFile = os.path.join('resume.txt')
user_name = #email
password = getpass.getpass('Enter your password: ')
recover(resumeFile)

matchObj1 = r"(\w*)( *)주간( *)연구( *)보고서( *)(\w*)"
matchObj2 = r"(\w*)( *)주간( *)보고서( *)(\w*)"
matchObj3 = r"(\w*)( *)[W|w]eekly( *)[R|r]eport( *)(\w*)"
matchKorean = r"(=?UTF-8?B?)(\w*)"
matchEmail = r"(\w+)@(\w+).(\w+)"

now = datetime.datetime.now()
data_path = os.getcwd() + "/data/"
dir_path = data_path + str(now.year) + '_' + sys.argv[1] + "week"

people = pd.read_csv(data_path + "people.csv", encoding="utf-8")
emptyTable = pd.DataFrame(0, index=range(0,len(people)), columns=["제출"])
hashTable = pd.concat([people["이름"], emptyTable], axis=1)
if not os.path.exists(dir_path):
    os.mkdir(dir_path)

for msg in GenerateMailMessages(user_name, password, resumeFile):
    if(isNotInWeek(msg['Date'], now)):
        break
    subject = UTFdecoder(msg['Subject'])
    if (re.search(matchObj1, subject) is None) and (re.search(matchObj2, subject) is None) and (re.search(matchObj2, subject) is None):
        continue
    print("\n------------------------------------\n")
    save_attachments(msg, dir_path)

print("\nENDED GET REPORT FROM EMAIL!")
print(hashTable)
hashTable.to_csv(dir_path + "/cur_submitter.csv", sep=',', encoding="utf-8", index=False)
os.remove(resumeFile)