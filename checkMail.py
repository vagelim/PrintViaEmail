#!/usr/bin/python
__author__ = 'vageli'
from imaplib import *
import os
import email
from printJob import *
import pymail

import mailHandler as mH #mail processing functions

path = os.path.dirname(os.path.abspath(__file__)) + '/'

detach_dir = path + 'detach'


def emailPrinter():
    #mailHander handles login, email processing and attachment downloading
    mHReturn = mH.mailHandler()
    username = mHReturn[0]
    filename = mHReturn[1]

    printJob(filename)#Send the filename to the printer

    subj = "Print Job Complete"
    message = filename + ' has been printed'
    pymail.mail(username,subj, message)#mail the client that job is complete


if __name__ == "__main__":
    emailPrinter()