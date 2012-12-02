#!/usr/bin/python
__author__ = 'vageli'
import os
import commands
path = os.path.dirname(os.path.abspath(__file__)) + '/'

detach_dir = '/tmp/detach/'

def printJob(file):
    print commands.getoutput("unoconv " + file)
    file = file[:file.find('.')] + '.pdf' #add pdf suffix to filename
    print commands.getoutput("lpr " + detach_dir + file)
    print commands.getoutput("rm *" + detach_dir)
    print commands.getoutput("rmdir " + detach_dir)