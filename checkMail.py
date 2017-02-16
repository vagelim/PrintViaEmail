#!/usr/bin/python
__author__ = 'vageli'
from __future__ import print_function
import httplib2
import os
import code
import base64
import subprocess

from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify', 'https://mail.google.com/']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Email to Printer'

# Download dir
STORAGE = os.path.dirname(os.path.abspath(__file__)) + "/download/"
# Printable extensions
FILE_EXTENSIONS = ['txt', 'pdf', 'doc', 'docx']
AUTHORIZED = ['']

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'email_to_printer.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def unreads(service):
    messages = service.users().messages().list( userId="me", q="in:unread").execute()
    return messages

def serviceMe():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service

def getAttachments(service, msg_id, store_dir=STORAGE, user_id="me"):
  """Get and store attachment from Message with given id.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    store_dir: The directory used to store attachments.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    subject = [x['value'] for x in message['payload']['headers'] if x['name'] == "Subject"][0]
    sender = [x['value'] for x in message['payload']['headers'] if x['name'] == "From"][0]

    #print ("{} {} ".format(subject, sender))
    # Only print from authorized senders
    valid = False
    for each in AUTHORIZED:
        if not valid:
            if sender.find(each) != -1:
                valid = True
    if valid:
        for part in message['payload']['parts']:
          if part['filename']:
            parts = part['filename'].split('.')

            if ((len(parts) == 2 ) #and parts[1][:-3] in FILE_EXTENSIONS
                or len(parts) == 1):

                attachmentId = part['body']['attachmentId']
                attach = service.users().messages().attachments().get(userId=user_id, id=attachmentId, messageId=msg_id).execute()
                file_data = base64.urlsafe_b64decode(attach['data']
                                                     .encode('UTF-8'))

                path = ''.join([store_dir, part['filename']])

                with open(path.encode('ascii'), 'w') as f:
                    f.write(file_data)
                print ("Wrote to {}".format(path))

  except KeyError:
    print ("Exception")

def markRead(service, messageId):
    removeLabels = {'removeLabelIds': ["UNREAD"]}
    result = service.users().messages().modify(
        userId="me", id=messageId, body=removeLabels).execute()

def readMail(service, messages):
    """
    arg: service | Service object
    arg: messages| Dict of messages
    eff: print email info
    eff: mark messages as read
    ret: void
    """

    # Process email
    size = messages['resultSizeEstimate']
    print ("{} messages found".format(size))
    if messages.get('messages', None) is None:
        return []

    # Create storage dir if not present
    if not os.path.exists(STORAGE):
        os.makedirs(STORAGE)

    # Process messages one by one
    for message in messages['messages']:
        messageId = message['id']
        message = service.users().messages().get(id=messageId, userId="me").execute()
        # Get attachments
        getAttachments(service, messageId)
        markRead(service, messageId)


def dummy(*args):
    pass

def printDownloads(filename=None, path=None, test=False):
    if test:
        subprocess.call = dummy
    toPrint = []

    if filename:
        toPrint.append(STORAGE + filename)
    elif path:
        toPrint.append(path)

    if toPrint:
        lpr =  subprocess.call(["/usr/bin/lpr", toPrint])
    else:
        for each in os.walk(STORAGE).next()[2]:
            path = STORAGE + each
            # Could be an empty dir
            if path:
                lpr =  subprocess.call(["/usr/bin/lpr", STORAGE + each])
                toPrint.append(STORAGE + each)

    print ("{} attachments".format(len(toPrint)))
    [os.remove(x) for x in toPrint if type(x) is not list]


if __name__ == '__main__':
    service = serviceMe()
    messages = unreads(service)
    readMail(service, messages)
    printDownloads()
