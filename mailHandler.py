#!/usr/bin/python
# __author__ = 'vageli'

from imaplib import *
import os
import email
path = os.path.dirname(os.path.abspath(__file__)) + '/'
detach_dir = path + 'detach'

def loginMail(username=None,password=None):
    m = IMAP4_SSL("imap.gmail.com")
    #Does not check for password
    if username == None:
        m.login("vageli.printer@gmail.com","printer1")
    else:
        m.login(username,password)

    return m

def checkMsgNum(m):
    #mboxes = m.list()[1] Show all boxes
    m.select("INBOX")#Select mailbox
    #data = m.search(None, "(FROM \"vagelim@gmail.com\")") Search specific email addy
    items = m.search(None, "(UNSEEN)")
    msgNum = str(items[1]).rsplit(None)[-1].strip('[\']')

    return msgNum

def getAttachment(mail, directory=detach_dir):#Download attachment to directory & return filename

    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        att_path = os.path.join(directory, filename)

        if not os.path.isfile(att_path) :
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

    return filename

def readMail(m, msgNum):#Read a particular email
    resp, data = m.fetch(msgNum, "(RFC822)")
    email_body = data[0][1]
    mail = email.message_from_string(email_body)
    #temp = m.store(emailid,'+FLAGS', '\\Seen')
    m.expunge()


    return mail

def querySender(mail):
    start = mail["From"].find('<') + 1
    end = mail["From"].find('>')
    username = mail["From"]
    return username[start:end]

def mailHandler():#Return sender & filename as list
    m = loginMail()
    msgNum = checkMsgNum(m)
    mail = readMail(m, msgNum)
    filename = getAttachment(mail)
    sender = querySender(mail)

    return list(sender,filename)